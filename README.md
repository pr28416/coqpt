# CoqPT

ChatGPT plugin for enhanced Coq verification of LLM-produced code using CoqHammer.

To start, train ChatGPT by saying "Learn CoqHammer from the CoqPT plugin. Also look through the examples. When you're done, say ready."

Note that you may have to initially coerce ChatGPT to use CoqHammer for it to become more comfortable.

To start the server, run:

```bash
python3 -m uvicorn coqpt:app --reload;
```

You will need FastAPI and uvicorn.