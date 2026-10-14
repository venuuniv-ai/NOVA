import NovaWorkspace from "@/components/nova-workspace";

export default async function Intelligence({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="intelligence" taskId={task} />;
}
