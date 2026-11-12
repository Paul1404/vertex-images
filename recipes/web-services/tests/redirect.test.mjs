import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';

const context = vm.createContext({});
vm.runInContext(readFileSync(new URL('../railway-sm-redaxo-origin/cloudfront-www-redirect.js', import.meta.url), 'utf8'), context);
const handler = context.handler;
const request = (host, uri = '/', querystring = {}, raw = '') => ({
  headers: { host: { value: host } }, uri, querystring,
  rawQueryString: () => raw,
});

test('apex requests pass through unchanged', () => {
  const input = request('schlossmuehle-untereuerheim.de');
  assert.equal(handler({ request: input }), input);
});
test('www redirects permanently and preserves the path and raw query', () => {
  const result = handler({ request: request('WWW.SCHLOSSMUEHLE-UNTEREUERHEIM.DE', '/index.php', {}, 'article_id=2&view=full') });
  assert.equal(result.statusCode, 308);
  assert.equal(result.headers.location.value, 'https://schlossmuehle-untereuerheim.de/index.php?article_id=2&view=full');
});
test('query fallback preserves repeated parameters', () => {
  const result = handler({ request: request('www.schlossmuehle-untereuerheim.de', '/', {
    tag: { multiValue: [{ value: 'a' }, { value: 'b' }] },
  }) });
  assert.equal(result.headers.location.value, 'https://schlossmuehle-untereuerheim.de/?tag=a&tag=b');
});
