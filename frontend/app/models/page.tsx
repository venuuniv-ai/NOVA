import NovaWorkspace from "@/components/nova-workspace";

export default async function Models({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="models" taskId={task} />;
}
