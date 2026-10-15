import EvaluationLab from "@/components/evaluation-lab";
export default async function Evals({searchParams}:{searchParams:Promise<{run?:string}>}){const {run}=await searchParams;return <EvaluationLab initialRun={run}/>;}
