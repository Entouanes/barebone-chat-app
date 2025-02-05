from blob_wrapper import BlobWrapper
from search_wrapper import SearchWrapper
import time

# Initialize search service
search_service = SearchWrapper()

# Initialize blob service
blob_service = BlobWrapper()

# main

if __name__ == "__main__":
    # Upload all files from the source directory (if any)
    blob_service.upload_all()

    # Create or update the search service configuration
    search_service.run_config_pipeline()
    
    # Wait for the indexer to finish
    time.sleep(30)

    # Query the search service
    print(list(search_service.search("puccini")))