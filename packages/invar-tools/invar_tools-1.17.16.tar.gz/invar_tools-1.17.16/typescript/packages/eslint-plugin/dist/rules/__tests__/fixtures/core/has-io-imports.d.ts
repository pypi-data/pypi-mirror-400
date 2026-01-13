/**
 * Invalid Core file - has I/O imports
 * Tests: no-io-in-core (should fail in /core/ directory)
 */
/**
 * Function that uses I/O (not allowed in Core)
 *
 * @example
 * readData('/path') // => 'data'
 */
export declare function readData(path: string): string;
//# sourceMappingURL=has-io-imports.d.ts.map