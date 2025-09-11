# Model Versions

I've been using OpenAI's models for this project due to how (relatively) easy they are to set up.
In particular, I've been using the `gpt-4o-mini` model for the agent LLMs due to its cost-effectiveness.

I've been getting much better results with `gpt-5`, but OpenAI requires you to 'verify' your account
by uploading a government-issued ID. Not only is this a bit of a pain, but I'm not really comfortable
with the idea of the company making the most magical device in the world having access to my
passport. This only affects streaming the results, so `gpt-5` is used for integration tests
running in CI to improve test accuracy.

## Note: Cost

I've spent about 52 cents on this project so far.
