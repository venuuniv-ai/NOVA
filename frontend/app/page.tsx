import NovaWorkspace from "@/components/nova-workspace";

export default async function Home({ searchParams }: { searchParams: Promise<{ task?: string }> }) {
  const { task } = await searchParams;
  return <NovaWorkspace view="command" taskId={task} />;
}
