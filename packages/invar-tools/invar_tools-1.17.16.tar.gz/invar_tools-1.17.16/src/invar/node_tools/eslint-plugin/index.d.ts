/**
 * @invar/eslint-plugin - ESLint plugin with Invar-specific rules
 *
 * Rules:
 * - @invar/require-schema-validation: Zod-typed params must have .parse()
 * - @invar/no-io-in-core: Forbid I/O imports in /core/ directories
 * - @invar/shell-result-type: Shell functions must return Result<T, E>
 * - @invar/no-any-in-schema: Forbid z.any() in schemas
 * - @invar/require-jsdoc-example: Exported functions need @example
 * - @invar/max-file-lines: Enforce max file length (layer-based)
 * - @invar/max-function-lines: Enforce max function length (layer-based)
 * - @invar/no-empty-schema: Forbid empty or permissive Zod schemas
 * - @invar/no-redundant-type-schema: Forbid schemas that only repeat TypeScript types
 * - @invar/require-complete-validation: All function params must be validated, or none
 * - @invar/no-runtime-imports: Forbid require()/import() inside functions
 * - @invar/no-impure-calls-in-core: Forbid Core importing from Shell
 * - @invar/no-pure-logic-in-shell: Warn when Shell contains pure logic
 * - @invar/shell-complexity: Warn when Shell functions are too complex
 * - @invar/thin-entry-points: Warn when entry points contain substantial logic
 */
import type { ESLint, Rule } from 'eslint';
declare const rules: Record<string, Rule.RuleModule>;
declare const configs: {
    recommended: {
        plugins: string[];
        rules: {
            '@invar/require-schema-validation': readonly ["error", {
                readonly mode: "recommended";
            }];
            '@invar/no-io-in-core': "error";
            '@invar/shell-result-type': "warn";
            '@invar/no-any-in-schema': "warn";
            '@invar/require-jsdoc-example': "error";
            '@invar/max-file-lines': "error";
            '@invar/max-function-lines': "warn";
            '@invar/no-empty-schema': "error";
            '@invar/no-redundant-type-schema': "warn";
            '@invar/require-complete-validation': "warn";
            '@invar/no-runtime-imports': "error";
            '@invar/no-impure-calls-in-core': "error";
            '@invar/no-pure-logic-in-shell': "warn";
            '@invar/shell-complexity': "warn";
            '@invar/thin-entry-points': "warn";
        };
    };
    strict: {
        plugins: string[];
        rules: {
            '@invar/require-schema-validation': readonly ["error", {
                readonly mode: "strict";
            }];
            '@invar/no-io-in-core': "error";
            '@invar/shell-result-type': "error";
            '@invar/no-any-in-schema': "error";
            '@invar/require-jsdoc-example': "error";
            '@invar/max-file-lines': "error";
            '@invar/max-function-lines': "error";
            '@invar/no-empty-schema': "error";
            '@invar/no-redundant-type-schema': "error";
            '@invar/require-complete-validation': "error";
            '@invar/no-runtime-imports': "error";
            '@invar/no-impure-calls-in-core': "error";
            '@invar/no-pure-logic-in-shell': "error";
            '@invar/shell-complexity': "error";
            '@invar/thin-entry-points': "error";
        };
    };
};
declare const plugin: ESLint.Plugin;
export default plugin;
export { rules, configs };
//# sourceMappingURL=index.d.ts.map