/**
 * Rule: no-pure-logic-in-shell
 *
 * Warn when Shell functions contain pure logic that should be in Core.
 * Shell functions should perform I/O operations, not pure computations.
 *
 * Heuristics for detecting pure logic:
 * - No async/await usage
 * - No I/O-related API calls (fs, http, fetch, db, etc.)
 * - No Result type in return
 * - Function body has more than 3 statements (substantial logic)
 */
import type { Rule } from 'eslint';
export declare const noPureLogicInShell: Rule.RuleModule;
export default noPureLogicInShell;
//# sourceMappingURL=no-pure-logic-in-shell.d.ts.map