import requests
from requests.adapters import HTTPAdapter, Retry
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Generic, TypeVar, Union
import structlog
from datetime import datetime
import uuid
from tqdm.auto import tqdm
import pandas as pd
import numpy as np
from io import StringIO
import threading

T = TypeVar('T')

# Constants used by helper functions
STANCE_MAP = {
    'Argument in Favor': 'Favor',
    'Argument Against': 'Against',
    'No Argument': 'NoArgument'
}

TOPIC_VALUES = {
    'No Topic': 'NoTopic',
    'no topic': 'NoTopic',
    'no-topic': 'NoTopic',
    'notopic': 'NoTopic'
}

@dataclass
class ClientConfig:
    """Configuration for the WIBA client"""
    environment: str = "production"
    log_level: str = "INFO"
    api_token: Optional[str] = None
    api_url: str = "https://wiba.dev"
    connect_timeout: float = 10.0  # Connection timeout in seconds
    read_timeout: float = 300.0    # Read timeout in seconds (5 min for large discover requests)

@dataclass
class ClientStatistics:
    """Statistics for API usage"""
    total_requests: int = 0
    method_calls: Dict[str, int] = field(default_factory=lambda: {
        'detect': 0,
        'extract': 0,
        'stance': 0,
        'comprehensive': 0,
        'discover_arguments': 0
    })
    last_request_timestamp: Optional[datetime] = None
    total_texts_processed: int = 0
    errors_encountered: int = 0

class WIBAError(Exception):
    """Base exception for WIBA client errors"""
    pass

class ValidationError(WIBAError):
    """Raised when input validation fails"""
    pass

@dataclass
class ResponseMetadata:
    """Metadata for API responses"""
    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0

@dataclass
class WIBAResponse(Generic[T]):
    """Generic response wrapper for all WIBA API responses"""
    data: T
    metadata: ResponseMetadata
    status: str = "success"
    errors: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ArgumentDetectionResult:
    """Result of argument detection for a single text"""
    text: str
    argument_prediction: str  # "Argument" or "NoArgument"
    confidence_score: float
    argument_components: Optional[Dict[str, Any]] = None

@dataclass
class TopicExtractionResult:
    """Result of topic extraction for a single text"""
    text: str
    topics: List[str]
    topic_metadata: Optional[Dict[str, Any]] = None

@dataclass
class StanceAnalysisResult:
    """Result of stance analysis for a text-topic pair"""
    text: str
    topic: str
    stance: str
    supporting_evidence: Optional[List[str]] = None

@dataclass
class ComprehensiveAnalysisResult:
    """Result of comprehensive argument analysis"""
    text: str
    is_argument: bool
    confidence: float
    topic_fine: str
    topic_broad: str
    stance_fine: str
    stance_broad: str
    argument_type: str
    argument_scheme: str
    claims: List[str]
    premises: List[str]

@dataclass
class SegmentResult:
    """Result of text segmentation"""
    original_id: int
    text_segment: str
    start_index: int
    end_index: int
    text: str
    processed_text: str
    parent_id: Optional[int] = None

@dataclass
class CalculatedSegmentResult:
    """Result of segment calculation"""
    id: int
    text: str
    processed_text: str
    text_segment: str
    start_index: int
    end_index: int
    argument_prediction: str  # "Argument" or "NoArgument"
    argument_confidence: float  # Confidence score for argument prediction
    original_id: int
    parent_id: Optional[int] = None

@dataclass
class ArgumentSegmentResult:
    """Result of argument discovery in text segments"""
    id: int
    text: str  # Original full text
    text_segment: str  # The segment text
    start_index: int  # Start index in sentences
    end_index: int  # End index in sentences
    argument_prediction: str  # "Argument" or "NoArgument"
    argument_confidence: float  # Confidence score for argument prediction
    overlapping_segments: List[str]  # IDs of overlapping segments
    processed_text: str  # Preprocessed text segment

class ResponseFactory:
    """Factory for creating response objects from raw API responses"""
    
    @staticmethod
    def create_detection_response(raw_response: Dict[str, Any], input_text: str) -> WIBAResponse[List[ArgumentDetectionResult]]:
        metadata = ResponseMetadata(
            request_id=str(uuid.uuid4()),
            processing_time=0.0
        )
        
        # API returns a list of dictionaries with argument_prediction and argument_confidence
        result = ArgumentDetectionResult(
            text=input_text,
            argument_prediction=raw_response[0]['argument_prediction'],
            confidence_score=raw_response[0]['argument_confidence'],
            argument_components=None
        )
        
        return WIBAResponse(data=[result], metadata=metadata)

    @staticmethod
    def create_extraction_response(raw_response: Dict[str, Any], input_text: str) -> WIBAResponse[List[TopicExtractionResult]]:
        metadata = ResponseMetadata(
            request_id=str(uuid.uuid4()),
            processing_time=0.0
        )
        
        # API returns a list of dictionaries with extracted_topic
        topic = raw_response[0]['extracted_topic']
        standardized_topic = TOPIC_VALUES.get(topic, topic)
        
        result = TopicExtractionResult(
            text=input_text,
            topics=[standardized_topic] if standardized_topic != 'NoTopic' else [],
            topic_metadata=None
        )
        
        return WIBAResponse(data=[result], metadata=metadata)

    @staticmethod
    def create_stance_response(raw_response: Dict[str, Any], input_text: str, input_topic: str) -> WIBAResponse[List[StanceAnalysisResult]]:
        metadata = ResponseMetadata(
            request_id=str(uuid.uuid4()),
            processing_time=0.0
        )
        
        # Use the class-level stance mapping
        stance_text = STANCE_MAP.get(raw_response[0]['stance_prediction'], raw_response[0]['stance_prediction'])
        
        result = StanceAnalysisResult(
            text=input_text,
            topic=input_topic,
            stance=stance_text,
            supporting_evidence=None
        )
        
        return WIBAResponse(data=[result], metadata=metadata)

class WIBA:
    """Client for interacting with the WIBA API"""
    
    # Add stance mapping at class level
    STANCE_MAP = {
        'Argument in Favor': 'Favor',
        'Argument Against': 'Against',
        'No Argument': 'NoArgument'
    }
    
    # Add standardized values as class constants
    ARGUMENT_VALUES = {
        'argument': 'Argument',
        'non-argument': 'NoArgument',
        'non_argument': 'NoArgument',
        'no-argument': 'NoArgument',
        'noargument': 'NoArgument'
    }
    
    TOPIC_VALUES = {
        'No Topic': 'NoTopic',
        'no topic': 'NoTopic',
        'no-topic': 'NoTopic',
        'notopic': 'NoTopic'
    }

    def __init__(self, api_token: Optional[str] = None, config: Optional[ClientConfig] = None, pool_connections: int = 100, pool_maxsize: int = 100):
        """Initialize the WIBA client.
        
        Args:
            api_token: API token for authentication
            config: Optional client configuration
            pool_connections: Number of urllib3 connection pools to cache
            pool_maxsize: Maximum number of connections to save in the pool
        """
        self.config = config or ClientConfig()
        
        # Set API token from either direct argument or config
        self.api_token = api_token or self.config.api_token
        if not self.api_token:
            raise ValidationError("API token is required. Provide it either through api_token parameter or ClientConfig.")
        
        # Initialize statistics
        self.statistics = ClientStatistics()
        
        # Set up structured logging
        self.logger = structlog.get_logger(
            "wiba",
            env=self.config.environment
        )

        # Initialize session with connection pooling and retry strategy
        self.session = self._create_session(pool_connections, pool_maxsize)
        
        # Thread-local storage for request-specific data
        self._thread_local = threading.local()

    def _create_session(self, pool_connections: int, pool_maxsize: int) -> requests.Session:
        """Create a new session with connection pooling and retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504, 429],  # Include rate limiting
            allowed_methods=["GET", "POST"]  # Allow retries on both GET and POST
        )
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,  # Number of urllib3 connection pools to cache
            pool_maxsize=pool_maxsize,  # Maximum number of connections to save in the pool
            max_retries=retries,
            pool_block=False  # Don't block when pool is full, raise error instead
        )
        
        # Mount adapter for both HTTP and HTTPS
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup."""
        self.close()

    def close(self):
        """Close the client and cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()

    def _get_request_id(self) -> str:
        """Get a thread-local request ID."""
        if not hasattr(self._thread_local, 'request_id'):
            self._thread_local.request_id = str(uuid.uuid4())
        return self._thread_local.request_id

    def _update_statistics(self, method_name: str, num_texts: int = 1, error: bool = False) -> None:
        """Update usage statistics.
        
        Args:
            method_name: Name of the method being called
            num_texts: Number of texts being processed
            error: Whether an error occurred
        """
        self.statistics.total_requests += 1
        self.statistics.method_calls[method_name] = self.statistics.method_calls.get(method_name, 0) + 1
        self.statistics.last_request_timestamp = datetime.utcnow()
        self.statistics.total_texts_processed += num_texts
        if error:
            self.statistics.errors_encountered += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get current usage statistics.
        
        Returns:
            Dictionary containing usage statistics in the server API format
        """
        # Calculate total API calls
        total_api_calls = sum(self.statistics.method_calls.values())
        
        # Calculate method percentages
        method_breakdown = {}
        for method, count in self.statistics.method_calls.items():
            method_breakdown[method] = {
                'count': count,
                'percentage': round((count / total_api_calls * 100) if total_api_calls > 0 else 0, 1)
            }
        
        # Ensure all methods have entries
        for method in ['detect', 'extract', 'stance', 'comprehensive', 'discover_arguments']:
            if method not in method_breakdown:
                method_breakdown[method] = {'count': 0, 'percentage': 0}
        
        return {
            'overview': {
                'total_api_calls': total_api_calls,
                'total_texts_processed': self.statistics.total_texts_processed,
                'last_request': self.statistics.last_request_timestamp.isoformat() if self.statistics.last_request_timestamp else None,
                'errors_encountered': self.statistics.errors_encountered
            },
            'method_breakdown': method_breakdown
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = self.config.api_url + endpoint
        
        # Extract method name from endpoint, removing 'api' prefix
        method_name = endpoint.split('/')[-1]
        
        # Add request ID and authentication for tracking
        request_id = self._get_request_id()
        request_headers = {
            "X-Request-ID": request_id,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "X-API-Token": self.api_token
        }
        if headers:
            request_headers.update(headers)
        
        try:
            # Only transform non-segment requests
            if data and endpoint not in ['/api/create_segments', '/api/calculate_segments', '/api/discover_arguments']:
                # Convert single text to list format for the API
                if 'text' in data:
                    json_data = {'texts': [data['text']]}
                elif 'texts' in data and isinstance(data['texts'], str):
                    json_data = {'texts': [data['texts']]}
                else:
                    json_data = data
            else:
                json_data = data
            
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                headers=request_headers,
                timeout=(self.config.connect_timeout, self.config.read_timeout)
            )
            
            # Handle all error cases
            if not response.ok:
                self._update_statistics(method_name, error=True)
                if response.status_code == 401:
                    raise ValidationError("Invalid API token")
                elif response.status_code == 403:
                    raise ValidationError("API token does not have sufficient permissions")
                elif response.status_code == 400:
                    raise ValidationError(f"Bad request: {response.text}")
                response.raise_for_status()
            
            # Update statistics on successful request
            num_texts = len(json_data.get('texts', [])) if isinstance(json_data, dict) and 'texts' in json_data else 1
            self._update_statistics(method_name, num_texts=num_texts)
            
            return response.json()
            
        except requests.exceptions.Timeout as e:
            self._update_statistics(method_name, error=True)
            raise WIBAError(
                f"Request timed out after {self.config.read_timeout}s. "
                f"For large texts, try increasing read_timeout in ClientConfig. Error: {str(e)}"
            )
        except requests.exceptions.RequestException as e:
            self._update_statistics(method_name, error=True)
            if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
                if e.response.status_code in (401, 403):
                    raise ValidationError(f"Authentication failed: {str(e)}")
            raise WIBAError(f"Request failed: {str(e)}")

    def _validate_dataframe(self, df: pd.DataFrame, required_columns: List[str]) -> None:
        """Validate DataFrame has required columns and non-empty data."""
        if not isinstance(df, pd.DataFrame):
            raise ValidationError("Input must be a pandas DataFrame")
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValidationError(f"DataFrame missing required columns: {missing_columns}")
        
        if df.empty:
            raise ValidationError("DataFrame is empty")
        
        # Check for null values in required columns
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            null_cols = null_counts[null_counts > 0].index.tolist()
            raise ValidationError(f"Null values found in columns: {null_cols}")

    def detect(self, texts: Union[str, List[str], pd.DataFrame], text_column: str = 'text', batch_size: int = 100, show_progress: bool = True) -> Union[ArgumentDetectionResult, List[ArgumentDetectionResult], pd.DataFrame]:
        """
        Detect arguments in text(s).
        
        Args:
            texts: Input text(s) - can be a single string, list of strings, or DataFrame
            text_column: Column name containing text if input is DataFrame
            batch_size: Number of texts to process in each batch for list/DataFrame inputs
            show_progress: Whether to show progress bar for batch processing
            
        Returns:
            Single result, list of results, or DataFrame depending on input type
        """
        try:
            # Handle DataFrame input
            if isinstance(texts, pd.DataFrame):
                self._validate_dataframe(texts, [text_column])
                texts_list = texts.copy()
                texts_to_process = texts_list[text_column].tolist()
                
                results = []
                with tqdm(total=len(texts_to_process), desc="Detecting arguments", disable=not show_progress) as pbar:
                    for i in range(0, len(texts_to_process), batch_size):
                        batch = texts_to_process[i:i + batch_size]
                        response = self._make_request("POST", "/api/detect", {"texts": batch})
                        
                        for text, result in zip(batch, response):
                            detection_result = ArgumentDetectionResult(
                                text=text,
                                argument_prediction=result['argument_prediction'],
                                confidence_score=result['argument_confidence'],
                                argument_components=None
                            )
                            results.append(detection_result)
                        pbar.update(len(batch))
                
                # Add results to DataFrame
                texts_list['argument_prediction'] = [r.argument_prediction for r in results]
                texts_list['argument_confidence'] = [r.confidence_score for r in results]
                return texts_list
            
            # Handle list input
            elif isinstance(texts, list):
                results = []
                with tqdm(total=len(texts), desc="Detecting arguments", disable=not show_progress) as pbar:
                    for i in range(0, len(texts), batch_size):
                        batch = texts[i:i + batch_size]
                        response = self._make_request("POST", "/api/detect", {"texts": batch})
                        
                        for text, result in zip(batch, response):
                            detection_result = ArgumentDetectionResult(
                                text=text,
                                argument_prediction=result['argument_prediction'],
                                confidence_score=result['argument_confidence'],
                                argument_components=None
                            )
                            results.append(detection_result)
                        pbar.update(len(batch))
                return results
            
            # Handle single string input
            elif isinstance(texts, str):
                response = self._make_request("POST", "/api/detect", {"texts": [texts]})
                return ArgumentDetectionResult(
                    text=texts,
                    argument_prediction=response[0]['argument_prediction'],
                    confidence_score=response[0]['argument_confidence'],
                    argument_components=None
                )
            
            else:
                raise ValidationError("Input must be a string, list of strings, or DataFrame")
                
        except Exception as e:
            raise

    def extract(self, texts: Union[str, List[str], pd.DataFrame], text_column: str = 'text', batch_size: int = 100, show_progress: bool = True) -> Union[TopicExtractionResult, List[TopicExtractionResult], pd.DataFrame]:
        """
        Extract topics from text(s).
        
        Args:
            texts: Input text(s) - can be a single string, list of strings, or DataFrame
            text_column: Column name containing text if input is DataFrame
            batch_size: Number of texts to process in each batch for list/DataFrame inputs
            show_progress: Whether to show progress bar for batch processing
            
        Returns:
            Single result, list of results, or DataFrame depending on input type
        """
        try:
            # Handle DataFrame input
            if isinstance(texts, pd.DataFrame):
                self._validate_dataframe(texts, [text_column])
                texts_list = texts.copy()
                texts_to_process = texts_list[text_column].tolist()
                
                results = []
                with tqdm(total=len(texts_to_process), desc="Extracting topics", disable=not show_progress) as pbar:
                    for i in range(0, len(texts_to_process), batch_size):
                        batch = texts_to_process[i:i + batch_size]
                        response = self._make_request("POST", "/api/extract", {"texts": batch})
                        
                        for text, result in zip(batch, response):
                            extraction_result = TopicExtractionResult(
                                text=text,
                                topics=[result['extracted_topic']] if result['extracted_topic'] != 'No Topic' else [],
                                topic_metadata=None
                            )
                            results.append(extraction_result)
                        pbar.update(len(batch))
                
                # Add results to DataFrame
                texts_list['extracted_topics'] = [','.join(r.topics) if r.topics else 'No Topic' for r in results]
                return texts_list
            
            # Handle list input
            elif isinstance(texts, list):
                results = []
                with tqdm(total=len(texts), desc="Extracting topics", disable=not show_progress) as pbar:
                    for i in range(0, len(texts), batch_size):
                        batch = texts[i:i + batch_size]
                        response = self._make_request("POST", "/api/extract", {"texts": batch})
                        
                        for text, result in zip(batch, response):
                            extraction_result = TopicExtractionResult(
                                text=text,
                                topics=[result['extracted_topic']] if result['extracted_topic'] != 'No Topic' else [],
                                topic_metadata=None
                            )
                            results.append(extraction_result)
                        pbar.update(len(batch))
                return results
            
            # Handle single string input
            elif isinstance(texts, str):
                response = self._make_request("POST", "/api/extract", {"text": texts})
                return TopicExtractionResult(
                    text=texts,
                    topics=[response[0]['extracted_topic']] if response[0]['extracted_topic'] != 'No Topic' else [],
                    topic_metadata=None
                )
            
            else:
                raise ValidationError("Input must be a string, list of strings, or DataFrame")
                
        except Exception as e:
            raise

    def stance(self, texts: Union[str, List[str], pd.DataFrame], topics: Union[str, List[str], None] = None, 
                      text_column: str = 'text', topic_column: str = 'topic', batch_size: int = 100, 
                      show_progress: bool = True) -> Union[StanceAnalysisResult, List[StanceAnalysisResult], pd.DataFrame]:
        """
        Analyze stance of text(s) in relation to topic(s).
        
        Args:
            texts: Input text(s) - can be a single string, list of strings, or DataFrame
            topics: Topic(s) - required unless input is DataFrame with topic_column
            text_column: Column name containing text if input is DataFrame
            topic_column: Column name containing topics if input is DataFrame
            batch_size: Number of texts to process in each batch for list/DataFrame inputs
            show_progress: Whether to show progress bar for batch processing
            
        Returns:
            Single result, list of results, or DataFrame depending on input type
        """
        try:
            # Handle DataFrame input
            if isinstance(texts, pd.DataFrame):
                self._validate_dataframe(texts, [text_column, topic_column])
                texts_list = texts.copy()
                texts_to_process = texts_list[text_column].tolist()
                topics_to_process = texts_list[topic_column].tolist()
                
                results = []
                with tqdm(total=len(texts_to_process), desc="Analyzing stances", disable=not show_progress) as pbar:
                    for i in range(0, len(texts_to_process), batch_size):
                        batch_texts = texts_to_process[i:i + batch_size]
                        batch_topics = topics_to_process[i:i + batch_size]
                        
                        response = self._make_request(
                            "POST", 
                            "/api/stance", 
                            {
                                "texts": batch_texts,
                                "topics": batch_topics
                            }
                        )
                        
                        for text, topic, result in zip(batch_texts, batch_topics, response):
                            stance_text = self.STANCE_MAP.get(result['stance_prediction'], result['stance_prediction'])
                            stance_result = StanceAnalysisResult(
                                text=text,
                                topic=topic,
                                stance=stance_text,
                                supporting_evidence=None
                            )
                            results.append(stance_result)
                        pbar.update(len(batch_texts))
                
                # Add results to DataFrame
                texts_list['stance'] = [r.stance for r in results]
                return texts_list
            
            # Handle list input
            elif isinstance(texts, list):
                if not topics or not isinstance(topics, list) or len(texts) != len(topics):
                    raise ValidationError("Must provide matching list of topics for list of texts")
                
                results = []
                with tqdm(total=len(texts), desc="Analyzing stances", disable=not show_progress) as pbar:
                    for i in range(0, len(texts), batch_size):
                        batch_texts = texts[i:i + batch_size]
                        batch_topics = topics[i:i + batch_size]
                        
                        response = self._make_request(
                            "POST", 
                            "/api/stance", 
                            {
                                "texts": batch_texts,
                                "topics": batch_topics
                            }
                        )
                        
                        for text, topic, result in zip(batch_texts, batch_topics, response):
                            stance_text = self.STANCE_MAP.get(result['stance_prediction'], result['stance_prediction'])
                            stance_result = StanceAnalysisResult(
                                text=text,
                                topic=topic,
                                stance=stance_text,
                                supporting_evidence=None
                            )
                            results.append(stance_result)
                        pbar.update(len(batch_texts))
                return results
            
            # Handle single string input
            elif isinstance(texts, str):
                if not topics or not isinstance(topics, str):
                    raise ValidationError("Must provide a topic string for single text input")
                    
                response = self._make_request(
                    "POST", 
                    "/api/stance", 
                    {
                        "texts": [texts],
                        "topics": [topics]
                    }
                )
                
                stance_text = self.STANCE_MAP.get(response[0]['stance_prediction'], response[0]['stance_prediction'])
                return StanceAnalysisResult(
                    text=texts,
                    topic=topics,
                    stance=stance_text,
                    supporting_evidence=None
                )
            
            else:
                raise ValidationError("Input must be a string, list of strings, or DataFrame")
                
        except Exception as e:
            raise

    def analyze_stance(self, texts: Union[str, List[str], pd.DataFrame], topics: Union[str, List[str], None] = None, 
                      text_column: str = 'text', topic_column: str = 'topic', batch_size: int = 100, 
                      show_progress: bool = True) -> Union[StanceAnalysisResult, List[StanceAnalysisResult], pd.DataFrame]:
        """Deprecated: Use stance() instead"""
        return self.stance(texts, topics, text_column=text_column, topic_column=topic_column, 
                         batch_size=batch_size, show_progress=show_progress)

    def process_csv(self, csv_data: Union[str, StringIO], text_column: str = 'text', topic_column: Optional[str] = None,
                   detect: bool = True, extract: bool = True, stance: bool = False, batch_size: int = 100) -> pd.DataFrame:
        """Process a CSV file through multiple analyses.
        
        Args:
            csv_data: CSV string or StringIO object
            text_column: Name of column containing text to analyze
            topic_column: Name of column containing topics (required for stance analysis)
            detect: Whether to perform argument detection
            extract: Whether to perform topic extraction
            stance: Whether to perform stance analysis
            batch_size: Number of texts to process in each batch
            
        Returns:
            DataFrame with results from all requested analyses
        """
        try:
            # Read CSV
            if isinstance(csv_data, str):
                df = pd.read_csv(StringIO(csv_data))
            else:
                df = pd.read_csv(csv_data)
            
            self._validate_dataframe(df, [text_column])
            
            # Perform requested analyses
            if detect:
                df = self.process_dataframe_detect(df, text_column, batch_size)
            
            if extract:
                df = self.process_dataframe_extract(df, text_column, batch_size)
            
            if stance:
                if not topic_column or topic_column not in df.columns:
                    raise ValidationError("Topic column required for stance analysis")
                df = self.process_dataframe_stance(df, text_column, topic_column, batch_size)
            
            return df
            
        except Exception as e:
            self.logger.error("CSV processing failed", error=str(e))
            raise

    def save_results(self, df: pd.DataFrame, output_path: str, format: str = 'csv') -> None:
        """Save results DataFrame to file.
        
        Args:
            df: DataFrame to save
            output_path: Path to save file
            format: Output format ('csv' or 'json')
        """
        try:
            if format.lower() == 'csv':
                df.to_csv(output_path, index=False)
            elif format.lower() == 'json':
                df.to_json(output_path, orient='records', lines=True)
            else:
                raise ValueError(f"Unsupported output format: {format}")
                
        except Exception as e:
            self.logger.error("Failed to save results", error=str(e))
            raise

    def process_dataframe_detect(self, df: pd.DataFrame, text_column: str = 'text', batch_size: int = 100) -> pd.DataFrame:
        """Deprecated: Use detect() instead"""
        return self.detect(df, text_column=text_column, batch_size=batch_size)

    def process_dataframe_extract(self, df: pd.DataFrame, text_column: str = 'text', batch_size: int = 100) -> pd.DataFrame:
        """Deprecated: Use extract() instead"""
        return self.extract(df, text_column=text_column, batch_size=batch_size)

    def process_dataframe_stance(self, df: pd.DataFrame, text_column: str = 'text', topic_column: str = 'topic', batch_size: int = 100) -> pd.DataFrame:
        """Deprecated: Use stance() instead"""
        return self.stance(df, text_column=text_column, topic_column=topic_column, batch_size=batch_size)

    def comprehensive(self, texts: Union[str, List[str], pd.DataFrame], text_column: str = 'text', batch_size: int = 100, show_progress: bool = True) -> Union['ComprehensiveAnalysisResult', List['ComprehensiveAnalysisResult'], pd.DataFrame]:
        """
        Perform comprehensive argument analysis including detection, topic extraction, stance analysis, and argument structure.
        
        Args:
            texts: Input text(s) - can be a single string, list of strings, or DataFrame
            text_column: Column name containing text if input is DataFrame
            batch_size: Number of texts to process in each batch for list/DataFrame inputs
            show_progress: Whether to show progress bar for batch processing
            
        Returns:
            Single result, list of results, or DataFrame depending on input type
        """
        try:
            # Handle DataFrame input
            if isinstance(texts, pd.DataFrame):
                self._validate_dataframe(texts, [text_column])
                texts_list = texts.copy()
                texts_to_process = texts_list[text_column].tolist()
                
                # Process in batches
                all_results = []
                with tqdm(total=len(texts), desc="Performing comprehensive analysis", disable=not show_progress) as pbar:
                    for i in range(0, len(texts), batch_size):
                        batch_texts = texts_to_process[i:i + batch_size]
                        batch_results = self._process_comprehensive_batch(batch_texts)
                        all_results.extend(batch_results)
                        pbar.update(len(batch_texts))
                
                # Add results to DataFrame
                result_df = pd.DataFrame(all_results)
                return pd.concat([texts_list, result_df], axis=1)
                
            # Handle list input
            elif isinstance(texts, list):
                all_results = []
                with tqdm(total=len(texts), desc="Performing comprehensive analysis", disable=not show_progress) as pbar:
                    for i in range(0, len(texts), batch_size):
                        batch = texts[i:i + batch_size]
                        batch_results = self._process_comprehensive_batch(batch)
                        all_results.extend([ComprehensiveAnalysisResult(**result, text=texts[idx]) 
                                           for idx, result in enumerate(batch_results)])
                        pbar.update(len(batch))
                
                return all_results
                
            # Handle single string input
            else:
                results = self._process_comprehensive_batch([texts])
                return ComprehensiveAnalysisResult(**results[0], text=texts)
                
        except Exception as e:
            self._update_statistics("comprehensive", error=True)
            self.logger.error("Comprehensive analysis failed", error=str(e))
            raise

    def _process_comprehensive_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of texts for comprehensive analysis."""
        request_data = {
            "texts": texts,
            "batch_size": min(len(texts), 100)
        }
        
        response = self._make_request('POST', '/api/comprehensive', data=request_data)
        self._update_statistics("comprehensive", num_texts=len(texts))
        
        # Process and clean results
        results = []
        for result in response:
            # Ensure all required fields are present
            cleaned_result = {
                'is_argument': result.get('is_argument', False),
                'confidence': result.get('confidence', 0.5),
                'topic_fine': result.get('topic_fine', 'NoTopic'),
                'topic_broad': result.get('topic_broad', 'NoTopic'), 
                'stance_fine': result.get('stance_fine', 'NoArgument'),
                'stance_broad': result.get('stance_broad', 'NoArgument'),
                'argument_type': result.get('argument_type', 'NoArgument'),
                'argument_scheme': result.get('argument_scheme', 'none_detected'),
                'claims': result.get('claims', []),
                'premises': result.get('premises', [])
            }
            results.append(cleaned_result)
        
        return results

    def discover_arguments(self, texts: Union[str, pd.DataFrame], text_column: str = 'text', window_size: int = 3,
                          step_size: int = 1, batch_size: int = 5, show_progress: bool = True,
                          max_text_length: int = 10000) -> pd.DataFrame:
        """
        Discover arguments in text(s) using sliding window technique with comprehensive analysis.

        Uses overlapping windows of sentences, evaluates each with comprehensive analysis,
        and selects best non-overlapping argument segments by confidence score.

        Args:
            texts: Input text(s) - can be a single string or DataFrame
            text_column: Column name containing text if input is DataFrame
            window_size: Size of the sliding window (number of sentences). Defaults to 3.
            step_size: Step size for the sliding window. Defaults to 1.
            batch_size: Number of texts to process in each batch for DataFrame input. Defaults to 5.
            show_progress: Whether to show progress bar for DataFrame input. Defaults to True.
            max_text_length: Maximum allowed length for each text. Defaults to 10000.

        Returns:
            pd.DataFrame: DataFrame containing discovered segments with columns:
                - id: Segment identifier
                - text: Original input text
                - text_segment: The segment text
                - start_index, end_index: Sentence indices in original text
                - is_argument: Boolean indicating if segment contains an argument
                - argument_prediction: 'Argument' or 'NoArgument'
                - argument_confidence: Confidence score (0-1)
                - claims: List of claims extracted from the argument
                - premises: List of premises extracted from the argument
                - topic_fine: Specific topic being argued
                - topic_broad: Broader policy category
                - stance_fine, stance_broad: Position on topics ('Favor'/'Against'/'NoArgument')
                - argument_type: Type of reasoning (Deductive/Inductive/etc.)
                - argument_scheme: Argumentation scheme (e.g., causal_argument)
                - overlapping_segments: IDs of other windows that overlapped with this one
        """
        try:
            # Handle DataFrame input
            if isinstance(texts, pd.DataFrame):
                self._validate_dataframe(texts, [text_column])
                texts_list = texts.copy()
                texts_to_process = texts_list[text_column].tolist()
                
                # Validate text lengths
                for text in texts_to_process:
                    if len(text) > max_text_length:
                        raise ValidationError(f"Text exceeds maximum length of {max_text_length} characters")
                
                all_results = []
                with tqdm(total=len(texts), desc="Discovering arguments", disable=not show_progress) as pbar:
                    # Process in batches
                    for i in range(0, len(texts), batch_size):
                        batch_texts = texts.iloc[i:i + batch_size]
                        batch_results = []
                        
                        # Process each text in the batch
                        for _, row in batch_texts.iterrows():
                            text = row[text_column]
                            result_df = self._discover_arguments_single(text, window_size, step_size)
                            
                            # Add original row data to results
                            for col in batch_texts.columns:
                                if col != text_column:
                                    result_df[col] = row[col]
                            
                            batch_results.append(result_df)
                        
                        # Add batch results and update progress
                        all_results.extend(batch_results)
                        pbar.update(len(batch_texts))
                
                # Combine all results
                return pd.concat(all_results, ignore_index=True)
            
            # Handle single string input
            elif isinstance(texts, str):
                if len(texts) > max_text_length:
                    raise ValidationError(f"Text exceeds maximum length of {max_text_length} characters")
                return self._discover_arguments_single(texts, window_size, step_size)
            
            else:
                raise ValidationError("Input must be a string or DataFrame")
                
        except Exception as e:
            raise
            
    def _discover_arguments_single(self, text: str, window_size: int, step_size: int) -> pd.DataFrame:
        """Internal method to discover arguments in a single text."""
        # Validate input
        if not text or not isinstance(text, str):
            raise ValidationError("Input text must be a non-empty string")
        if window_size < 1:
            raise ValidationError("window_size must be greater than 0")
        if step_size < 1:
            raise ValidationError("step_size must be greater than 0")
        
        # Prepare request data in the format expected by the server
        request_data = {
            "text": text,
            "params": {
                "window_size": window_size,
                "step_size": step_size,
                "min_segment_length": 1,
                "max_segment_length": 100,
                "overlap": True
            }
        }
        
        try:
            # Make request to discover arguments
            response = self._make_request(
                method="POST",
                endpoint="/api/discover_arguments",
                data=request_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Request-ID": str(uuid.uuid4())
                }
            )
        
            # Convert response to DataFrame
            if isinstance(response, list):
                result_df = pd.DataFrame(response)
            else:
                result_df = pd.DataFrame([response])
            
            # Ensure all required columns are present
            required_columns = [
                'id', 'text', 'text_segment', 'start_index', 'end_index',
                'is_argument', 'argument_prediction', 'argument_confidence',
                'processed_text', 'overlapping_segments'
            ]

            # Comprehensive analysis fields (for argument segments)
            comprehensive_columns = [
                'claims', 'premises', 'topic_fine', 'topic_broad',
                'stance_fine', 'stance_broad', 'argument_type', 'argument_scheme'
            ]

            for col in required_columns:
                if col not in result_df.columns:
                    if col == 'overlapping_segments':
                        result_df[col] = [[] for _ in range(len(result_df))]
                    elif col == 'is_argument':
                        result_df[col] = False
                    elif col == 'argument_prediction':
                        # If segment_type exists, use it to set argument_prediction
                        if 'segment_type' in result_df.columns:
                            result_df[col] = result_df['segment_type'].apply(
                                lambda x: self.ARGUMENT_VALUES.get(str(x).lower(), 'NoArgument')
                            )
                        else:
                            result_df[col] = 'NoArgument'
                    else:
                        result_df[col] = None

            # Set defaults for comprehensive fields if not present
            for col in comprehensive_columns:
                if col not in result_df.columns:
                    if col in ['claims', 'premises']:
                        result_df[col] = [[] for _ in range(len(result_df))]
                    elif col in ['topic_fine', 'topic_broad']:
                        result_df[col] = 'NoTopic'
                    elif col in ['stance_fine', 'stance_broad', 'argument_type']:
                        result_df[col] = 'NoArgument'
                    elif col == 'argument_scheme':
                        result_df[col] = 'none_detected'

            # Standardize argument prediction values using class constant
            result_df['argument_prediction'] = result_df['argument_prediction'].apply(
                lambda x: self.ARGUMENT_VALUES.get(str(x).lower(), 'NoArgument')
            )

            # Remove redundant columns if they exist
            columns_to_drop = ['segment_type']
            result_df = result_df.drop(columns=[col for col in columns_to_drop if col in result_df.columns])
            
            # Sort by start_index and argument_confidence
            result_df = result_df.sort_values(
                ['start_index', 'argument_confidence'],
                ascending=[True, False]
            )
            
            return result_df
            
        except Exception as e:
            raise WIBAError(f"Failed to discover arguments: {str(e)}") 