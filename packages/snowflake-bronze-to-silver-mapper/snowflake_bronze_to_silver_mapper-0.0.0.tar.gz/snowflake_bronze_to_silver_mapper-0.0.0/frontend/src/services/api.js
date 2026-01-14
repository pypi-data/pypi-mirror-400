const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Pipeline CRUD operations
  async createPipeline(pipelineData) {
    const response = await fetch(`${API_BASE_URL}/api/pipelines`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pipelineData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create pipeline');
    }
    return response.json();
  },

  async getPipelines(domain = null) {
    const url = domain 
      ? `${API_BASE_URL}/api/pipelines?domain=${domain}`
      : `${API_BASE_URL}/api/pipelines`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch pipelines');
    return response.json();
  },

  async getPipeline(pipelineId) {
    const response = await fetch(`${API_BASE_URL}/api/pipelines/${pipelineId}`);
    if (!response.ok) throw new Error('Pipeline not found');
    return response.json();
  },

  async updatePipeline(pipelineId, pipelineData) {
    const response = await fetch(`${API_BASE_URL}/api/pipelines/${pipelineId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pipelineData)
    });
    if (!response.ok) throw new Error('Failed to update pipeline');
    return response.json();
  },

  async deletePipeline(pipelineId) {
    const response = await fetch(`${API_BASE_URL}/api/pipelines/${pipelineId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete pipeline');
    return response.json();
  },

  async executePipeline(pipelineId) {
    const response = await fetch(`${API_BASE_URL}/api/pipelines/${pipelineId}/execute`, {
      method: 'POST'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Pipeline execution failed');
    }
    return response.json();
  },

  async getPipelineRuns(pipelineId, limit = 10) {
    const response = await fetch(`${API_BASE_URL}/api/pipelines/${pipelineId}/runs?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch pipeline runs');
    return response.json();
  },

  async exportConfig() {
    const response = await fetch(`${API_BASE_URL}/api/pipelines/export/config`);
    if (!response.ok) throw new Error('Failed to export config');
    return response.json();
  },

  // Snowflake operations
  async listTables(schema = null) {
    const url = schema
      ? `${API_BASE_URL}/api/snowflake/tables?schema=${schema}`
      : `${API_BASE_URL}/api/snowflake/tables`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch tables');
    return response.json();
  },

  async executeQuery(query) {
    const response = await fetch(`${API_BASE_URL}/api/snowflake/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!response.ok) throw new Error('Query execution failed');
    return response.json();
  }
};