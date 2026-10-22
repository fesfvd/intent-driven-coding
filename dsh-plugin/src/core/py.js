/**
 * Byte-compatible helpers for the Python reference implementation.
 *
 * The IDC event log is written with `json.dumps(..., ensure_ascii=False,
 * sort_keys=True)`, and the derived index with `json.dump(..., indent=2,
 * ensure_ascii=False, sort_keys=True)`. Node's JSON.stringify uses different
 * separators, so parity tests need these encoders.
 */

export function pyJsonDumps(value) {
  return encodeCompact(value);
}

export function pyJsonPretty(value) {
  return encodePretty(value, 0);
}

function encodeCompact(value) {
  if (value === null) return 'null';
  const type = typeof value;
  if (type === 'boolean') return value ? 'true' : 'false';
  if (type === 'number') return encodeNumber(value);
  if (type === 'string') return encodeString(value);
  if (Array.isArray(value)) return '[' + value.map(encodeCompact).join(', ') + ']';
  if (type === 'object') {
    const keys = Object.keys(value).sort();
    return '{' + keys.map((key) => encodeString(key) + ': ' + encodeCompact(value[key])).join(', ') + '}';
  }
  throw new TypeError(`cannot serialize ${type}`);
}

function encodePretty(value, level) {
  const pad = '  '.repeat(level);
  const childPad = '  '.repeat(level + 1);
  if (value === null) return 'null';
  const type = typeof value;
  if (type === 'boolean') return value ? 'true' : 'false';
  if (type === 'number') return encodeNumber(value);
  if (type === 'string') return encodeString(value);
  if (Array.isArray(value)) {
    if (value.length === 0) return '[]';
    const items = value.map((item) => childPad + encodePretty(item, level + 1));
    return '[\n' + items.join(',\n') + '\n' + pad + ']';
  }
  if (type === 'object') {
    const keys = Object.keys(value).sort();
    if (keys.length === 0) return '{}';
    const items = keys.map((key) => childPad + encodeString(key) + ': ' + encodePretty(value[key], level + 1));
    return '{\n' + items.join(',\n') + '\n' + pad + '}';
  }
  throw new TypeError(`cannot serialize ${type}`);
}

function encodeNumber(value) {
  if (!Number.isFinite(value)) {
    if (Number.isNaN(value)) return 'NaN';
    return value > 0 ? 'Infinity' : '-Infinity';
  }
  if (Number.isInteger(value) && Math.abs(value) <= Number.MAX_SAFE_INTEGER) return String(value);
  return String(value);
}

function encodeString(value) {
  let out = '"';
  for (const char of value) {
    switch (char) {
      case '"':
        out += '\\"';
        break;
      case '\\':
        out += '\\\\';
        break;
      case '\b':
        out += '\\b';
        break;
      case '\f':
        out += '\\f';
        break;
      case '\n':
        out += '\\n';
        break;
      case '\r':
        out += '\\r';
        break;
      case '\t':
        out += '\\t';
        break;
      default: {
        const code = char.codePointAt(0);
        if (code < 0x20) out += '\\u' + code.toString(16).padStart(4, '0');
        else if (code >= 0xd800 && code <= 0xdfff) out += '\\u' + code.toString(16).padStart(4, '0');
        else out += char;
      }
    }
  }
  return out + '"';
}

/** Python `datetime.now(timezone.utc).isoformat()` for a JS Date. */
export function isoformat(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (!Number.isFinite(date.getTime())) throw new Error('invalid date');
  const pad = (number, width = 2) => String(number).padStart(width, '0');
  const base =
    `${pad(date.getUTCFullYear(), 4)}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}` +
    `T${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}`;
  const micros = date.getUTCMilliseconds() * 1000;
  return micros === 0 ? `${base}+00:00` : `${base}.${pad(micros, 6)}+00:00`;
}

/** Python `datetime.fromisoformat` for the ISO-8601 shapes IDC stores. */
export function parseIsoformat(text) {
  if (typeof text !== 'string') throw new Error('invalid ISO-8601 value');
  const date = new Date(text);
  if (!Number.isFinite(date.getTime())) throw new Error(`invalid ISO-8601 value: ${text}`);
  return date;
}

/** Python `round(value, digits)` (half-even) for metrics fields. */
export function pythonRound(value, digits = 0) {
  if (!Number.isFinite(value)) return value;
  const factor = 10 ** digits;
  const scaled = value * factor;
  const floor = Math.floor(scaled);
  const fraction = scaled - floor;
  const tolerance = Number.EPSILON * Math.max(1, Math.abs(scaled)) * 4;
  let rounded;
  if (Math.abs(fraction - 0.5) <= tolerance) {
    rounded = floor % 2 === 0 ? floor : floor + 1;
  } else {
    rounded = Math.round(scaled);
  }
  return rounded / factor;
}

/** Python `str.splitlines()` for UTF-8 text. */
export function splitLines(text) {
  if (text === '') return [];
  const lines = text.split(/\r\n|[\n\r\u000b\u000c\u001c\u001d\u001e\u0085\u2028\u2029]/);
  if (lines.length > 0 && lines[lines.length - 1] === '') lines.pop();
  return lines;
}
