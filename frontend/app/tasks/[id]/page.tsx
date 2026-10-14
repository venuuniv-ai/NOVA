import NovaWorkspace from "@/components/nova-workspace";

export default async function TaskDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <NovaWorkspace view="detail" taskId={id} />;
}
