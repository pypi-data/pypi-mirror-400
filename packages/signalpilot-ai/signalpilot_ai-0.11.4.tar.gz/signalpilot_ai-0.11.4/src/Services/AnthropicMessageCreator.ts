import Anthropic from '@anthropic-ai/sdk';
import { AppStateService } from '../AppState';
import { KernelPreviewUtils } from '../utils/kernelPreview';
import { TOOL_SEARCH_CONFIG, getSkillsContainer } from './SkillsConfig';

export interface IMessageCreationParams {
  client: Anthropic;
  modelName: string;
  systemPrompt: string;
  systemPromptAskMode: string;
  systemPromptFastMode: string;
  systemPromptWelcome: string;
  isFastMode: boolean;
  toolBlacklist: string[];
  mode: 'agent' | 'ask' | 'fast' | 'welcome';
  tools: any[];
  autoRun: boolean;
  systemPromptMessages?: string[];
  fetchNotebookState?: () => Promise<string>;
  notebookContextManager?: any;
  notebookId?: string;
  abortSignal: AbortSignal;
  errorLogger?: (message: any) => Promise<void>;
  customHeaders?: Record<string, string>;
}

export interface IPreparedMessages {
  initialMessages: any[];
  filteredHistory: any[];
  availableTools: any[];
  systemPrompt: string;
  extraSystemMessages: any[];
}

/**
 * Handles message preparation and stream creation for Anthropic API
 */
export class AnthropicMessageCreator {
  /**
   * Prepares messages and creates a stream
   */
  static async createMessageStream(
    params: IMessageCreationParams,
    filteredHistory: any[],
    normalizeMessageContent: (
      messages: any[],
      errorLogger?: (message: any) => Promise<void>
    ) => any[]
  ): Promise<any> {
    const perfStart = performance.now();
    console.log('[PERF] AnthropicMessageCreator.createMessageStream - START');

    const prepared = await this.prepareMessages(
      params,
      filteredHistory,
      normalizeMessageContent
    );
    const messages = [...prepared.initialMessages, ...prepared.filteredHistory];
    // Use claude-sonnet-4-5 for welcome messages only
    const modelToUse =
      params.mode === 'welcome' && messages.length === 1
        ? 'claude-sonnet-4-5'
        : params.modelName;

    console.log('[AnthropicMessageCreator] Using model:', modelToUse);

    const perfBeforeApiCall = performance.now();
    console.log(
      `[PERF] AnthropicMessageCreator.createMessageStream - Making API call (${(perfBeforeApiCall - perfStart).toFixed(2)}ms elapsed)`
    );

    // Prepare container with skills if available
    const skillsContainer = await getSkillsContainer();

    // Debug: Log skills container
    if (skillsContainer) {
      console.log(
        '[DEBUG] Skills container:',
        JSON.stringify(skillsContainer, null, 2)
      );
    } else {
      console.log('[DEBUG] No skills container - skills disabled');
    }

    // Add code execution tool (required for beta API)
    // TODO: Disabled because it's conflicting with the terminal-execute_command tool
    // const codeExecutionTool = {
    //   type: 'code_execution_20250825',
    //   name: 'code_execution'
    // };
    const finalTools = [...prepared.availableTools];
    console.log('[DEBUG] Added code execution tool for beta API');

    // Debug: Log final API parameters
    console.log('[DEBUG] Final API call parameters:');
    console.log('- Model:', modelToUse);
    console.log('- Beta headers:', TOOL_SEARCH_CONFIG.betaHeaders);
    console.log(
      '- Container parameter:',
      skillsContainer ? 'INCLUDED' : 'NOT INCLUDED'
    );
    console.log('- Tools count:', finalTools.length);

    return params.client.beta.messages.stream(
      {
        model: modelToUse,
        messages: [...prepared.initialMessages, ...prepared.filteredHistory],
        tools: finalTools.length > 0 ? finalTools : undefined,
        max_tokens: 4096,
        system: [
          {
            text: prepared.systemPrompt,
            type: 'text',
            cache_control: {
              type: 'ephemeral'
            }
          },
          ...prepared.extraSystemMessages
        ] as Anthropic.Beta.Messages.BetaTextBlockParam[],
        betas: TOOL_SEARCH_CONFIG.betaHeaders,
        // TODO: Disabled because it's conflicting with the terminal-execute_command tool
        // ...(skillsContainer && { container: skillsContainer as any }),
        tool_choice:
          finalTools.length > 0
            ? {
                type: 'auto',
                disable_parallel_tool_use: false
              }
            : undefined
      } as any,
      {
        signal: params.abortSignal,
        headers: {
          ...(params.customHeaders || {}),
          'no-cors': 'true',
          'sec-fetch-mode': 'no-cors',
          mode: 'no-cors'
        }
      }
    );
  }

  /**
   * Prepares all messages and configuration for the API call
   */
  private static async prepareMessages(
    params: IMessageCreationParams,
    filteredHistory: any[],
    normalizeMessageContent: (
      messages: any[],
      errorLogger?: (message: any) => Promise<void>
    ) => any[]
  ): Promise<IPreparedMessages> {
    // Get notebook context
    const contextCellsContent = await this.getNotebookContext(params);

    // Prepare initial messages
    const initialMessages = this.prepareInitialMessages(contextCellsContent);

    // Normalize messages
    const normalizedInitialMessages = normalizeMessageContent(
      initialMessages,
      params.errorLogger
    );
    const normalizedFilteredHistory = normalizeMessageContent(
      filteredHistory,
      params.errorLogger
    );

    // Determine system prompt
    const systemPrompt = this.determineSystemPrompt(params);

    // Filter tools for fast mode
    const availableTools = this.filterTools(params);

    // Prepare extra system messages
    const extraSystemMessages = await this.prepareExtraSystemMessages(params);

    return {
      initialMessages: normalizedInitialMessages,
      filteredHistory: normalizedFilteredHistory,
      availableTools,
      systemPrompt,
      extraSystemMessages
    };
  }

  /**
   * Gets notebook context if available
   */
  private static async getNotebookContext(
    params: IMessageCreationParams
  ): Promise<string> {
    try {
      if (params.notebookContextManager && params.notebookId) {
        return params.notebookContextManager.formatContextAsMessage(
          params.notebookId
        );
      }
    } catch (error) {
      await params.errorLogger?.({
        message: 'Error getting notebook context',
        error: error instanceof Error ? error.message : error,
        notebookPath: params.notebookId,
        notebookContextManager: !!params.notebookContextManager
      });
    }
    return '';
  }

  /**
   * Prepares initial messages with context
   */
  private static prepareInitialMessages(contextCellsContent: string): any[] {
    const initialMessages = [];

    if (contextCellsContent && contextCellsContent.trim() !== '') {
      initialMessages.push({
        role: 'user',
        content: contextCellsContent
      });
    }

    return initialMessages;
  }

  /**
   * Determines which system prompt to use
   */
  private static determineSystemPrompt(params: IMessageCreationParams): string {
    let basePrompt: string;

    if (params.mode === 'ask') {
      basePrompt = params.systemPromptAskMode;
    } else if (params.mode === 'fast') {
      basePrompt = params.systemPromptFastMode;
    } else if (params.mode === 'welcome') {
      basePrompt = params.systemPromptWelcome;
    } else {
      basePrompt = params.systemPrompt;
    }

    // Add auto-run mode instructions if enabled
    if (params.autoRun) {
      basePrompt +=
        '\n\nYou are in auto-run mode. wait_for_user_reply is not callable. Ignore other portions of prompt that require you to wait or confirm steps with the user. Continue until the problem is solved.';
    }

    return basePrompt;
  }

  /**
   * Filters tools based on fast mode settings and auto-run mode
   */
  private static filterTools(params: IMessageCreationParams): any[] {
    let filteredTools = params.tools;

    // Filter out blacklisted tools
    if (params.toolBlacklist.length > 0) {
      filteredTools = filteredTools.filter(
        tool => tool.name && !params.toolBlacklist.includes(tool.name)
      );
    }

    // Filter out wait_user_reply when auto-run is enabled
    if (params.autoRun) {
      filteredTools = filteredTools.filter(
        tool => tool.name !== 'notebook-wait_user_reply'
      );
    }

    return filteredTools;
  }

  /**
   * Prepares extra system messages
   */
  private static async prepareExtraSystemMessages(
    params: IMessageCreationParams
  ): Promise<any[]> {
    const perfStart = performance.now();
    console.log('[PERF] prepareExtraSystemMessages - START');

    const extraSystemMessages: any[] = [];

    // Add system prompt messages
    const perfSystemPrompt = performance.now();
    if (params.systemPromptMessages) {
      extraSystemMessages.push(
        ...params.systemPromptMessages.map(msg => ({
          text: msg,
          type: 'text'
        }))
      );
    }
    console.log(
      `[PERF] prepareExtraSystemMessages - System prompts added (${(performance.now() - perfSystemPrompt).toFixed(2)}ms)`
    );

    // Add workspace context for welcome mode
    const perfWorkspace = performance.now();
    if (params.mode === 'welcome') {
      const workspaceContext = AppStateService.getWorkspaceContext();
      if (workspaceContext && workspaceContext.welcome_context) {
        extraSystemMessages.push({
          type: 'text',
          text: `Workspace File System Context:\n\n${workspaceContext.welcome_context}`
        });
        console.log(
          '[AnthropicMessageCreator] Added workspace context to welcome mode system messages'
        );
      }
    }
    console.log(
      `[PERF] prepareExtraSystemMessages - Workspace context added (${(performance.now() - perfWorkspace).toFixed(2)}ms)`
    );

    // Add inserted snippets context
    const perfSnippets = performance.now();
    const insertedSnippets = AppStateService.getInsertedSnippets();
    if (insertedSnippets.length > 0) {
      const snippetsContext = insertedSnippets
        .map(
          snippet =>
            `Snippet Title: ${snippet.title}\nSnippet Description: ${snippet.description ? `${snippet.description}\n` : ''} === Begin ${snippet.title} Content === \n\n${snippet.content}\n\n=== END ${snippet.title} Content ===`
        )
        .join('\n\n');

      extraSystemMessages.push({
        type: 'text',
        text: `The user has inserted the following code snippets for context:\n\n${snippetsContext}`
      });
    }
    console.log(
      `[PERF] prepareExtraSystemMessages - Snippets added (${(performance.now() - perfSnippets).toFixed(2)}ms)`
    );

    // Add notebook state
    const perfNotebookState = performance.now();
    if (params.fetchNotebookState) {
      try {
        console.log(
          '[PERF] prepareExtraSystemMessages - Starting fetchNotebookState() call'
        );
        const perfBeforeFetch = performance.now();
        const notebookState = await params.fetchNotebookState();
        const perfAfterFetch = performance.now();
        console.log(
          `[PERF] prepareExtraSystemMessages - fetchNotebookState() returned (${(perfAfterFetch - perfBeforeFetch).toFixed(2)}ms)`
        );

        if (notebookState) {
          const perfBeforePush = performance.now();
          extraSystemMessages.push({
            type: 'text',
            text: `This is the current notebook summary with edit history: ${notebookState}`
          });
          console.log(
            `[PERF] prepareExtraSystemMessages - Notebook state pushed to messages (${(performance.now() - perfBeforePush).toFixed(2)}ms, state length: ${notebookState.length} chars)`
          );
        }
      } catch (error) {
        await params.errorLogger?.({
          message: 'Error fetching notebook state',
          error: error instanceof Error ? error.message : error,
          fetchNotebookState: !!params.fetchNotebookState
        });
      }
    }
    console.log(
      `[PERF] prepareExtraSystemMessages - Notebook state added (${(performance.now() - perfNotebookState).toFixed(2)}ms total)`
    );

    // Add kernel variables and objects preview
    const perfKernelPreview = performance.now();
    try {
      const kernelPreview = await KernelPreviewUtils.getLimitedKernelPreview();
      console.log('KERNEL PREVIEW:', kernelPreview);

      const dburl = AppStateService.getState().settings.databaseUrl;

      if (kernelPreview) {
        extraSystemMessages.push({
          type: 'text',
          text: `Current Kernel Variables and Objects Preview:\n\n${kernelPreview.replace(dburl, '<DB_URL>')}`
        });
      }
    } catch (error) {
      console.warn(
        '[AnthropicMessageCreator] Error getting kernel preview:',
        error
      );
      await params.errorLogger?.({
        message: 'Error getting kernel preview',
        error: error instanceof Error ? error.message : error
      });
    }
    console.log(
      `[PERF] prepareExtraSystemMessages - Kernel preview added (${(performance.now() - perfKernelPreview).toFixed(2)}ms)`
    );

    const perfEnd = performance.now();
    console.log(
      `[PERF] prepareExtraSystemMessages - COMPLETE (${(perfEnd - perfStart).toFixed(2)}ms total)`
    );

    return extraSystemMessages;
  }
}
