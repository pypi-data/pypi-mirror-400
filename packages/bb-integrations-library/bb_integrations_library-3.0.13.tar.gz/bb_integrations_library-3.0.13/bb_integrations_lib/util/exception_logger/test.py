from exception_logger import ExceptionLogger

# Create a logger instance
logger = ExceptionLogger()


# Example class using the exception logger
class DataProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.processed_count = 0

    @logger.catch_exceptions(identifier_param='record_id')
    def process_record(self, record_id, data):
        """Process a single data record"""
        if not data:
            raise ValueError(f"No data provided for record {record_id}")

        if 'amount' not in data:
            raise KeyError(f"Missing required field 'amount' in record {record_id}")

        # Process the record
        result = data['amount'] * 2
        self.processed_count += 1
        return result


# Multiple loggers for different components
api_logger = ExceptionLogger()
db_logger = ExceptionLogger()


# Example API function using a different logger
@api_logger.catch_exceptions()
def api_request(endpoint, payload=None):
    if not endpoint:
        raise ValueError("Endpoint cannot be empty")

    if endpoint == "/error":
        raise ConnectionError("Simulated API error")

    return {"status": "success", "data": payload}


# Example database function using yet another logger
@db_logger.catch_exceptions(identifier_param='query_id')
def execute_query(query_id, sql, parameters=None):
    if not sql:
        raise ValueError("SQL query cannot be empty")

    if "DROP TABLE" in sql.upper():
        raise PermissionError("DROP TABLE operations are not allowed")

    return [{"id": 1, "name": "Example"}]


# Main demonstration
def main():
    print("=== Data Processing Example ===")
    processor = DataProcessor(logger)
    records = [
        {'id': '001', 'data': {'amount': 100}},
        {'id': '002', 'data': {}},  # Missing 'amount' field
        {'id': '003', 'data': None},  # None data
        {'id': '004', 'data': {'amount': 200}}
    ]

    # Process each record and handle exceptions
    for record in records:
        try:
            result = processor.process_record(record['id'], record['data'])
            print(f"Record {record['id']} processed successfully: {result}")
        except Exception as e:
            print(f"Error processing record {record['id']}: {e}")

    print("\n=== API Example ===")
    endpoints = ["/users", "/error", ""]
    for endpoint in endpoints:
        try:
            result = api_request(endpoint, {"user": "test"})
            print(f"API request to {endpoint} succeeded: {result}")
        except Exception as e:
            print(f"API request to {endpoint} failed: {e}")

    print("\n=== Database Example ===")
    queries = [
        ("Q1", "SELECT * FROM users", None),
        ("Q2", "", None),  # Empty query
        ("Q3", "DROP TABLE users", None)  # Not allowed
    ]

    for query_id, sql, params in queries:
        try:
            result = execute_query(query_id, sql, params)
            print(f"Query {query_id} executed successfully: {result}")
        except Exception as e:
            print(f"Query {query_id} failed: {e}")

    # Print summary information
    print("\n=== Exception Logs ===")
    print("Data Processing Exceptions:", logger.get_exception_count())
    print("Exception Types:", logger.get_exceptions_by_type())
    print("\nAPI Exceptions:", api_logger.get_exception_count())
    print("Exception Types:", api_logger.get_exceptions_by_type())
    print("\nDatabase Exceptions:", db_logger.get_exception_count())
    print("Exception Types:", db_logger.get_exceptions_by_type())

    # Print detailed logs
    print("\n=== Detailed Data Processing Exception Log ===")
    print(logger.get_formatted_log())


if __name__ == "__main__":
    main()