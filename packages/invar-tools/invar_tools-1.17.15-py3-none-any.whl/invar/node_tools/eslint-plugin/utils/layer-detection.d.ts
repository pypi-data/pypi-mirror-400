/**
 * Layer Detection Utilities
 *
 * Detects which architectural layer a file belongs to:
 * - Core: Pure logic, strict limits
 * - Shell: I/O operations, relaxed limits
 * - Tests: Test files, most relaxed limits
 * - Default: Other files
 */
export type Layer = 'core' | 'shell' | 'tests' | 'default';
export interface LayerLimits {
    maxFileLines: number;
    maxFunctionLines: number;
}
/**
 * Default limits for each layer (LX-10).
 *
 * TypeScript limits = Python limits × 1.3 (due to type overhead).
 * - Python Core: 500/50 → TypeScript Core: 650/65
 * - Python Shell: 700/100 → TypeScript Shell: 910/130
 * - Python Tests: 1000/200 → TypeScript Tests: 1300/260
 * - Python Default: 600/80 → TypeScript Default: 780/104
 */
export declare const LAYER_LIMITS: Record<Layer, LayerLimits>;
/**
 * Detect layer from filename.
 *
 * Priority: tests > core > shell > default
 *
 * @example
 * getLayer('/project/src/core/parser.ts') // => 'core'
 * getLayer('/project/tests/parser.test.ts') // => 'tests'
 * getLayer('/project/src/shell/io.ts') // => 'shell'
 */
export declare function getLayer(filename: string): Layer;
/**
 * Get limits for a filename.
 *
 * @example
 * getLimits('/project/src/core/parser.ts')
 * // => { maxFileLines: 650, maxFunctionLines: 65 }
 */
export declare function getLimits(filename: string): LayerLimits;
//# sourceMappingURL=layer-detection.d.ts.map