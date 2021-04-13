# Change Log

## April 13, 2021

1. Added image comparisons using the `pixelmatch` library: <https://github.com/whtsky/pixelmatch-py>
2. Added signals and signal receivers to decouple POST request with image comparison
3. Mixed in with celery to add asynchronous processing for image comparison, multiple requests will be handled asynchronously separate from the django server
4. Multiprocessing (4 process so far, but can change upon discussion with team) has been added, making image comparison much faster

### NOTES

To make image comparisons faster, the images are scaled down before comparison by a factor of 4
