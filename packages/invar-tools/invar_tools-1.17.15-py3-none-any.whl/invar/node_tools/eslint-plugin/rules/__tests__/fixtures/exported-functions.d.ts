/**
 * Test require-jsdoc-example rule
 * Tests exported functions and arrow functions
 */
/**
 * Valid: Exported function with @example
 *
 * @example
 * validFunction() // => 'valid'
 */
export declare function validFunction(): string;
/**
 * Invalid: Exported function WITHOUT @example
 */
export declare function invalidFunction(): string;
/**
 * Valid: Exported arrow function with @example
 *
 * @example
 * validArrow() // => 'valid'
 */
export declare const validArrow: () => string;
/**
 * Invalid: Exported arrow function WITHOUT @example
 */
export declare const invalidArrow: () => string;
//# sourceMappingURL=exported-functions.d.ts.map