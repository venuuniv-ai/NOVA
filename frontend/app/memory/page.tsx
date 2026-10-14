import NovaWorkspace from "@/components/nova-workspace";

export default async function Memory({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="memory" taskId={task} />;
}
