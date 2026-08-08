export interface CodingProblem {
  id: number;
  title: string;
  description: string;
  difficulty?: string;
  time_complexity?: string;
  space_complexity?: string;
  hint?: string;
  ai_explanation?: string;
  java_solution?: string;
  python_solution?: string;
  cpp_solution?: string;
  javascript_solution?: string;
}
