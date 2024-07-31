# Running model locally:

Step 1) Install Llama.cpp
```
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build
cd build
cmake .. -DCMAKE_APPLE_SILICON_PROCESSOR=arm64 
make -j
```

Step 2) Download a GGUF format model
I have used [mistral-7b-instruct-v0.1.Q6_K.gguf](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/tree/main?show_file_info=mistral-7b-instruct-v0.1.Q6_K.gguf)

Step 3) In the build/bin is the llama-server binary
I have used the command 
```./build/bin/llama-server --color --model "../model/mistral-7b-instruct-v0.1.Q6_K.gguf" -t 7 -b 24 -n -1 --temp 0.3 -ngl 1```
For more information about options usable: https://github.com/ggerganov/llama.cpp
