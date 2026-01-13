/**
 * @invar/ts-analyzer - TypeScript contract analysis using Compiler API
 *
 * Provides deep analysis of TypeScript code including:
 * - Cross-file type tracing
 * - z.infer<T> resolution
 * - Contract quality assessment
 * - Blind spot detection (unvalidated critical code)
 */
import * as ts from 'typescript';
import { z } from 'zod';
export declare const ContractQualitySchema: z.ZodEnum<["strong", "medium", "weak", "useless"]>;
export type ContractQuality = z.infer<typeof ContractQualitySchema>;
export declare const ParamContractSchema: z.ZodObject<{
    name: z.ZodString;
    type: z.ZodString;
    hasContract: z.ZodBoolean;
    contractSource: z.ZodOptional<z.ZodObject<{
        schema: z.ZodOptional<z.ZodString>;
        file: z.ZodOptional<z.ZodString>;
        line: z.ZodOptional<z.ZodNumber>;
        traceChain: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        schema?: string | undefined;
        file?: string | undefined;
        line?: number | undefined;
        traceChain?: string[] | undefined;
    }, {
        schema?: string | undefined;
        file?: string | undefined;
        line?: number | undefined;
        traceChain?: string[] | undefined;
    }>>;
    quality: z.ZodOptional<z.ZodObject<{
        score: z.ZodEnum<["strong", "medium", "weak", "useless"]>;
        hasTypeConstraint: z.ZodBoolean;
        hasValueConstraint: z.ZodBoolean;
        hasBoundaryConstraint: z.ZodBoolean;
    }, "strip", z.ZodTypeAny, {
        score: "strong" | "medium" | "weak" | "useless";
        hasTypeConstraint: boolean;
        hasValueConstraint: boolean;
        hasBoundaryConstraint: boolean;
    }, {
        score: "strong" | "medium" | "weak" | "useless";
        hasTypeConstraint: boolean;
        hasValueConstraint: boolean;
        hasBoundaryConstraint: boolean;
    }>>;
}, "strip", z.ZodTypeAny, {
    type: string;
    name: string;
    hasContract: boolean;
    contractSource?: {
        schema?: string | undefined;
        file?: string | undefined;
        line?: number | undefined;
        traceChain?: string[] | undefined;
    } | undefined;
    quality?: {
        score: "strong" | "medium" | "weak" | "useless";
        hasTypeConstraint: boolean;
        hasValueConstraint: boolean;
        hasBoundaryConstraint: boolean;
    } | undefined;
}, {
    type: string;
    name: string;
    hasContract: boolean;
    contractSource?: {
        schema?: string | undefined;
        file?: string | undefined;
        line?: number | undefined;
        traceChain?: string[] | undefined;
    } | undefined;
    quality?: {
        score: "strong" | "medium" | "weak" | "useless";
        hasTypeConstraint: boolean;
        hasValueConstraint: boolean;
        hasBoundaryConstraint: boolean;
    } | undefined;
}>;
export type ParamContract = z.infer<typeof ParamContractSchema>;
export declare const FunctionAnalysisSchema: z.ZodObject<{
    name: z.ZodString;
    file: z.ZodString;
    line: z.ZodNumber;
    contractStatus: z.ZodEnum<["complete", "partial", "missing"]>;
    params: z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        type: z.ZodString;
        hasContract: z.ZodBoolean;
        contractSource: z.ZodOptional<z.ZodObject<{
            schema: z.ZodOptional<z.ZodString>;
            file: z.ZodOptional<z.ZodString>;
            line: z.ZodOptional<z.ZodNumber>;
            traceChain: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        }, "strip", z.ZodTypeAny, {
            schema?: string | undefined;
            file?: string | undefined;
            line?: number | undefined;
            traceChain?: string[] | undefined;
        }, {
            schema?: string | undefined;
            file?: string | undefined;
            line?: number | undefined;
            traceChain?: string[] | undefined;
        }>>;
        quality: z.ZodOptional<z.ZodObject<{
            score: z.ZodEnum<["strong", "medium", "weak", "useless"]>;
            hasTypeConstraint: z.ZodBoolean;
            hasValueConstraint: z.ZodBoolean;
            hasBoundaryConstraint: z.ZodBoolean;
        }, "strip", z.ZodTypeAny, {
            score: "strong" | "medium" | "weak" | "useless";
            hasTypeConstraint: boolean;
            hasValueConstraint: boolean;
            hasBoundaryConstraint: boolean;
        }, {
            score: "strong" | "medium" | "weak" | "useless";
            hasTypeConstraint: boolean;
            hasValueConstraint: boolean;
            hasBoundaryConstraint: boolean;
        }>>;
    }, "strip", z.ZodTypeAny, {
        type: string;
        name: string;
        hasContract: boolean;
        contractSource?: {
            schema?: string | undefined;
            file?: string | undefined;
            line?: number | undefined;
            traceChain?: string[] | undefined;
        } | undefined;
        quality?: {
            score: "strong" | "medium" | "weak" | "useless";
            hasTypeConstraint: boolean;
            hasValueConstraint: boolean;
            hasBoundaryConstraint: boolean;
        } | undefined;
    }, {
        type: string;
        name: string;
        hasContract: boolean;
        contractSource?: {
            schema?: string | undefined;
            file?: string | undefined;
            line?: number | undefined;
            traceChain?: string[] | undefined;
        } | undefined;
        quality?: {
            score: "strong" | "medium" | "weak" | "useless";
            hasTypeConstraint: boolean;
            hasValueConstraint: boolean;
            hasBoundaryConstraint: boolean;
        } | undefined;
    }>, "many">;
    returnType: z.ZodOptional<z.ZodString>;
    hasRuntimeValidation: z.ZodBoolean;
    validationLocations: z.ZodArray<z.ZodObject<{
        method: z.ZodString;
        line: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        line: number;
        method: string;
    }, {
        line: number;
        method: string;
    }>, "many">;
    jsdocExample: z.ZodBoolean;
}, "strip", z.ZodTypeAny, {
    params: {
        type: string;
        name: string;
        hasContract: boolean;
        contractSource?: {
            schema?: string | undefined;
            file?: string | undefined;
            line?: number | undefined;
            traceChain?: string[] | undefined;
        } | undefined;
        quality?: {
            score: "strong" | "medium" | "weak" | "useless";
            hasTypeConstraint: boolean;
            hasValueConstraint: boolean;
            hasBoundaryConstraint: boolean;
        } | undefined;
    }[];
    name: string;
    file: string;
    line: number;
    contractStatus: "complete" | "partial" | "missing";
    hasRuntimeValidation: boolean;
    validationLocations: {
        line: number;
        method: string;
    }[];
    jsdocExample: boolean;
    returnType?: string | undefined;
}, {
    params: {
        type: string;
        name: string;
        hasContract: boolean;
        contractSource?: {
            schema?: string | undefined;
            file?: string | undefined;
            line?: number | undefined;
            traceChain?: string[] | undefined;
        } | undefined;
        quality?: {
            score: "strong" | "medium" | "weak" | "useless";
            hasTypeConstraint: boolean;
            hasValueConstraint: boolean;
            hasBoundaryConstraint: boolean;
        } | undefined;
    }[];
    name: string;
    file: string;
    line: number;
    contractStatus: "complete" | "partial" | "missing";
    hasRuntimeValidation: boolean;
    validationLocations: {
        line: number;
        method: string;
    }[];
    jsdocExample: boolean;
    returnType?: string | undefined;
}>;
export type FunctionAnalysis = z.infer<typeof FunctionAnalysisSchema>;
export declare const BlindSpotSchema: z.ZodObject<{
    function: z.ZodString;
    file: z.ZodString;
    line: z.ZodNumber;
    risk: z.ZodEnum<["critical", "high", "medium", "low"]>;
    reason: z.ZodString;
    suggestedSchema: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    function: string;
    file: string;
    line: number;
    risk: "medium" | "critical" | "high" | "low";
    reason: string;
    suggestedSchema?: string | undefined;
}, {
    function: string;
    file: string;
    line: number;
    risk: "medium" | "critical" | "high" | "low";
    reason: string;
    suggestedSchema?: string | undefined;
}>;
export type BlindSpot = z.infer<typeof BlindSpotSchema>;
export declare const AnalysisResultSchema: z.ZodObject<{
    files: z.ZodNumber;
    functions: z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        file: z.ZodString;
        line: z.ZodNumber;
        contractStatus: z.ZodEnum<["complete", "partial", "missing"]>;
        params: z.ZodArray<z.ZodObject<{
            name: z.ZodString;
            type: z.ZodString;
            hasContract: z.ZodBoolean;
            contractSource: z.ZodOptional<z.ZodObject<{
                schema: z.ZodOptional<z.ZodString>;
                file: z.ZodOptional<z.ZodString>;
                line: z.ZodOptional<z.ZodNumber>;
                traceChain: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
            }, "strip", z.ZodTypeAny, {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            }, {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            }>>;
            quality: z.ZodOptional<z.ZodObject<{
                score: z.ZodEnum<["strong", "medium", "weak", "useless"]>;
                hasTypeConstraint: z.ZodBoolean;
                hasValueConstraint: z.ZodBoolean;
                hasBoundaryConstraint: z.ZodBoolean;
            }, "strip", z.ZodTypeAny, {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            }, {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            }>>;
        }, "strip", z.ZodTypeAny, {
            type: string;
            name: string;
            hasContract: boolean;
            contractSource?: {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            } | undefined;
            quality?: {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            } | undefined;
        }, {
            type: string;
            name: string;
            hasContract: boolean;
            contractSource?: {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            } | undefined;
            quality?: {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            } | undefined;
        }>, "many">;
        returnType: z.ZodOptional<z.ZodString>;
        hasRuntimeValidation: z.ZodBoolean;
        validationLocations: z.ZodArray<z.ZodObject<{
            method: z.ZodString;
            line: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            line: number;
            method: string;
        }, {
            line: number;
            method: string;
        }>, "many">;
        jsdocExample: z.ZodBoolean;
    }, "strip", z.ZodTypeAny, {
        params: {
            type: string;
            name: string;
            hasContract: boolean;
            contractSource?: {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            } | undefined;
            quality?: {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            } | undefined;
        }[];
        name: string;
        file: string;
        line: number;
        contractStatus: "complete" | "partial" | "missing";
        hasRuntimeValidation: boolean;
        validationLocations: {
            line: number;
            method: string;
        }[];
        jsdocExample: boolean;
        returnType?: string | undefined;
    }, {
        params: {
            type: string;
            name: string;
            hasContract: boolean;
            contractSource?: {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            } | undefined;
            quality?: {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            } | undefined;
        }[];
        name: string;
        file: string;
        line: number;
        contractStatus: "complete" | "partial" | "missing";
        hasRuntimeValidation: boolean;
        validationLocations: {
            line: number;
            method: string;
        }[];
        jsdocExample: boolean;
        returnType?: string | undefined;
    }>, "many">;
    coverage: z.ZodObject<{
        total: z.ZodNumber;
        withContracts: z.ZodNumber;
        percent: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        total: number;
        withContracts: number;
        percent: number;
    }, {
        total: number;
        withContracts: number;
        percent: number;
    }>;
    quality: z.ZodObject<{
        strong: z.ZodNumber;
        medium: z.ZodNumber;
        weak: z.ZodNumber;
        useless: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        strong: number;
        medium: number;
        weak: number;
        useless: number;
    }, {
        strong: number;
        medium: number;
        weak: number;
        useless: number;
    }>;
    blindSpots: z.ZodArray<z.ZodObject<{
        function: z.ZodString;
        file: z.ZodString;
        line: z.ZodNumber;
        risk: z.ZodEnum<["critical", "high", "medium", "low"]>;
        reason: z.ZodString;
        suggestedSchema: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        function: string;
        file: string;
        line: number;
        risk: "medium" | "critical" | "high" | "low";
        reason: string;
        suggestedSchema?: string | undefined;
    }, {
        function: string;
        file: string;
        line: number;
        risk: "medium" | "critical" | "high" | "low";
        reason: string;
        suggestedSchema?: string | undefined;
    }>, "many">;
    dependencies: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodArray<z.ZodString, "many">>>;
}, "strip", z.ZodTypeAny, {
    quality: {
        strong: number;
        medium: number;
        weak: number;
        useless: number;
    };
    files: number;
    functions: {
        params: {
            type: string;
            name: string;
            hasContract: boolean;
            contractSource?: {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            } | undefined;
            quality?: {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            } | undefined;
        }[];
        name: string;
        file: string;
        line: number;
        contractStatus: "complete" | "partial" | "missing";
        hasRuntimeValidation: boolean;
        validationLocations: {
            line: number;
            method: string;
        }[];
        jsdocExample: boolean;
        returnType?: string | undefined;
    }[];
    coverage: {
        total: number;
        withContracts: number;
        percent: number;
    };
    blindSpots: {
        function: string;
        file: string;
        line: number;
        risk: "medium" | "critical" | "high" | "low";
        reason: string;
        suggestedSchema?: string | undefined;
    }[];
    dependencies?: Record<string, string[]> | undefined;
}, {
    quality: {
        strong: number;
        medium: number;
        weak: number;
        useless: number;
    };
    files: number;
    functions: {
        params: {
            type: string;
            name: string;
            hasContract: boolean;
            contractSource?: {
                schema?: string | undefined;
                file?: string | undefined;
                line?: number | undefined;
                traceChain?: string[] | undefined;
            } | undefined;
            quality?: {
                score: "strong" | "medium" | "weak" | "useless";
                hasTypeConstraint: boolean;
                hasValueConstraint: boolean;
                hasBoundaryConstraint: boolean;
            } | undefined;
        }[];
        name: string;
        file: string;
        line: number;
        contractStatus: "complete" | "partial" | "missing";
        hasRuntimeValidation: boolean;
        validationLocations: {
            line: number;
            method: string;
        }[];
        jsdocExample: boolean;
        returnType?: string | undefined;
    }[];
    coverage: {
        total: number;
        withContracts: number;
        percent: number;
    };
    blindSpots: {
        function: string;
        file: string;
        line: number;
        risk: "medium" | "critical" | "high" | "low";
        reason: string;
        suggestedSchema?: string | undefined;
    }[];
    dependencies?: Record<string, string[]> | undefined;
}>;
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
export declare const ImpactAnalysisSchema: z.ZodObject<{
    file: z.ZodString;
    directDependents: z.ZodArray<z.ZodString, "many">;
    transitiveDependents: z.ZodArray<z.ZodString, "many">;
    impactLevel: z.ZodEnum<["low", "medium", "high", "critical"]>;
}, "strip", z.ZodTypeAny, {
    file: string;
    directDependents: string[];
    transitiveDependents: string[];
    impactLevel: "medium" | "critical" | "high" | "low";
}, {
    file: string;
    directDependents: string[];
    transitiveDependents: string[];
    impactLevel: "medium" | "critical" | "high" | "low";
}>;
export type ImpactAnalysis = z.infer<typeof ImpactAnalysisSchema>;
export declare const AnalyzerOptionsSchema: z.ZodObject<{
    path: z.ZodDefault<z.ZodString>;
    includePrivate: z.ZodDefault<z.ZodBoolean>;
    verbose: z.ZodDefault<z.ZodBoolean>;
    buildDependencyGraph: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    path: string;
    includePrivate: boolean;
    verbose: boolean;
    buildDependencyGraph: boolean;
}, {
    path?: string | undefined;
    includePrivate?: boolean | undefined;
    verbose?: boolean | undefined;
    buildDependencyGraph?: boolean | undefined;
}>;
export type AnalyzerOptions = z.infer<typeof AnalyzerOptionsSchema>;
/**
 * Build a dependency graph from TypeScript program.
 * Maps each file to the files it imports.
 */
declare function buildDependencyGraph(program: ts.Program): Record<string, string[]>;
/**
 * Analyze the impact of changing a specific file.
 *
 * @param file - The file being changed
 * @param graph - Dependency graph from buildDependencyGraph
 * @returns Impact analysis with dependents and severity
 */
export declare function analyzeImpact(file: string, graph: Record<string, string[]>): ImpactAnalysis;
/**
 * Analyze a TypeScript project for contract coverage.
 *
 * @param options - Analysis options
 * @returns Analysis result with function contracts and blind spots
 *
 * @example
 * ```typescript
 * import { analyze } from '@invar/ts-analyzer';
 *
 * const result = await analyze({ path: './my-project' });
 * console.log(`Coverage: ${result.coverage.percent}%`);
 * console.log(`Blind spots: ${result.blindSpots.length}`);
 * ```
 */
export declare function analyze(options?: Partial<AnalyzerOptions>): AnalysisResult;
export { buildDependencyGraph };
export default analyze;
//# sourceMappingURL=index.d.ts.map