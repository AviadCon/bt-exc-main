# Submission

## What I did

1. add the huggingface api call using the hf lib. update poetry.lock. 
2. make it possible to handle video files.
3. different handling for video and audio files for more efficiency.
4. did a CR to claude - he made a lot of basic sytax error and overthinking I had to change. (due to not having a ready claude.md with orders)

---

## HuggingFace integration

<!-- How you implemented _get_transcription(), any decisions you made, how you handle errors -->

At first I saw that the model is not capable of handling video files,
so I checked for ways to extract the audio files from it,
I found that I can use the ffprobe tool that already installed for extracting the wav file only and then use the HF model - this way its way more efficience because its not transfering the whole unnecasery video data throgh the network.


---

## Bonus work (if any)

more usage of OOP and file managment - I believe this is the right way to observe order and make the code easier to test and change.

Added health checks to rabbit and mongo by opening a connection and see they are connectable, if there is an error it will show in the response of the route which will be good for observation tools in the future.

Usage of pydantic baseModel for stractured responses from the API and more detailed swagger (openAPI) docs for future users and programmers on this project.

Waiting between worker jobs to avoid HF rate limits.

Dropzone for easy file upload.

new styling and UI stracture - tab navigation for admin actions ( with no security for now , just for demo)
---

## What I'd do next

<!-- If this were a real production service, what would you improve or add? -->

make a middleware that will convert every exception into a detailed log with extra params such as code line and file etc...

make a detailed claude.md file with the teams coding schemas and apply it into the project.

for the mongo , I would have create a DAL class and then a service class.

more detailed tests.

make a fallback queue for failed uploads


---

## System design question

**If 1,000 jobs were submitted simultaneously, what would break first in this system and why? What would you change to handle that load?**

<!-- Answer in 5–10 sentences. Be specific. -->
The FastAPI server - it handles a lot of file storing which will be resource heavy and because its not managed in shared storage , raising more pods wont help.

I would have add a S3 bucket and presigned urls, so the upload will occure from the client side.
I will add another route for sending the presigned urls.
I will still save the /upload route in order to get the file_id to pass it to the worker and update the state manager.
extra benefit: this way I will be able to fetch the file with some metadata to procceed with my video/audio detection and reduce more job from the worker.  

---

## Time spent

3 hours
