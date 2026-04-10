process.env.WORKSPACE_ROOT = 'G:/community agnts/community agents';
const module = await import('file:///G:/community%20agnts/community%20agents/openclaw-for-community/skills/CommunityIntegrationSkill/scripts/community_integration.mjs');
const { buildCommunityMessage, loadSavedCommunityState } = module;
const state = loadSavedCommunityState();
const sendContext = {
  group_id: state.groupId,
  thread_id: 'thread-1',
  parent_message_id: 'parent-1',
  task_id: 'task-1',
};
const payload = {
  message_type: 'analysis',
  semantics: { kind: 'analysis', intent: 'inform' },
  content: {
    text: 'reply text',
  },
};
const message = buildCommunityMessage(state, sendContext, payload);
console.log('stateGroup', state.groupId);
console.log(JSON.stringify(message, null, 2));
