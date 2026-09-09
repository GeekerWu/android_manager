const { setupBrowserRuntime } = await import('file:///C:/Users/Administrator/.codex/plugins/cache/openai-bundled/browser/26.616.81150/scripts/browser-client.mjs');
await setupBrowserRuntime({ globals: globalThis });
globalThis.browser = await agent.browsers.get('iab');
nodeRepl.write(await browser.documentation());