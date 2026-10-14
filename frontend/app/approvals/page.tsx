import NovaWorkspace from "@/components/nova-workspace";

export default async function Approvals({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="approvals" taskId={task} />;
}
