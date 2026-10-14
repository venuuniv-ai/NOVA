import NovaWorkspace from "@/components/nova-workspace";

export default async function Perception({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="perception" taskId={task} />;
}
