# Discord Message for Pipecat Dev Server

Hey Pipecat community! 👋

I've built **Voiceground** - an observability tool to help you hit **sub-1-second response times** by identifying bottlenecks in your voice pipelines.

## What it does

After each conversation, you get an **interactive HTML report** with:
- 📈 **Timeline visualization** of all events (STT, LLM, TTS, tool calls)
- 🔍 **Per-turn metrics** breakdown (Response Time, STT Latency, LLM TTFB, TTS Latency)
- 🎯 **Event highlighting** - hover over metrics to see related events in the timeline

## How it helps

The post-conversation analysis shows you exactly where time is spent, making it easy to:
- Identify bottlenecks (slow LLM TTFB? TTS taking too long?)
- Compare turns to see what's working vs. what's not
- Optimize iteratively to hit that <1s target

## Quick start

See the [quick start guide](https://github.com/poseneror/voiceground#quick-start) in the repo - just add the observer to your pipeline and you're good to go!

## Current status

Designed for **local development** - generates static HTML reports perfect for debugging and optimization.

**Open source**: https://github.com/poseneror/voiceground

Would love your feedback and suggestions! 🚀
