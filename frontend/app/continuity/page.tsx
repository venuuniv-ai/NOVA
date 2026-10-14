import NovaWorkspace from "@/components/nova-workspace";

export default async function Continuity({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="continuity" taskId={task} />;
}
