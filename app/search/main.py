from blob_wrapper import BlobWrapper
from search_wrapper import SearchWrapper

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

    # Perform a test search:
    search_service.search("When was WestSide Story performed for the first time at the New York Philharmonic?")