/**
 * Valid Shell file - I/O imports allowed
 * Tests: no-io-in-core (should pass in /shell/ directory)
 */
/**
 * Shell function with I/O operations
 *
 * @example
 * readConfig('/path') // => { ... }
 */
export declare function readConfig(path: string): object;
/**
 * Shell function with HTTP operations
 *
 * @example
 * fetchData('url') // => Promise<data>
 */
export declare function fetchData(url: string): Promise<unknown>;
//# sourceMappingURL=with-io.d.ts.map