import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'c47'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/fine-tuning-cant-fix-hallucinations',
    component: ComponentCreator('/blog/fine-tuning-cant-fix-hallucinations', '00b'),
    exact: true
  },
  {
    path: '/blog/formal-verification-cot',
    component: ComponentCreator('/blog/formal-verification-cot', '9b4'),
    exact: true
  },
  {
    path: '/blog/how-qwed-verifies-math-sympy',
    component: ComponentCreator('/blog/how-qwed-verifies-math-sympy', '907'),
    exact: true
  },
  {
    path: '/blog/introducing-qwed',
    component: ComponentCreator('/blog/introducing-qwed', '45c'),
    exact: true
  },
  {
    path: '/blog/llms-translators-not-calculators',
    component: ComponentCreator('/blog/llms-translators-not-calculators', '2e7'),
    exact: true
  },
  {
    path: '/blog/page/2',
    component: ComponentCreator('/blog/page/2', '9de'),
    exact: true
  },
  {
    path: '/blog/qwed-cicd-integration',
    component: ComponentCreator('/blog/qwed-cicd-integration', '646'),
    exact: true
  },
  {
    path: '/blog/qwed-crewai-agents',
    component: ComponentCreator('/blog/qwed-crewai-agents', 'dee'),
    exact: true
  },
  {
    path: '/blog/qwed-langchain-integration',
    component: ComponentCreator('/blog/qwed-langchain-integration', '6e1'),
    exact: true
  },
  {
    path: '/blog/secure-code-execution-docker',
    component: ComponentCreator('/blog/secure-code-execution-docker', 'a5b'),
    exact: true
  },
  {
    path: '/blog/sql-injection-ast-parsing',
    component: ComponentCreator('/blog/sql-injection-ast-parsing', '12b'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/ai-safety',
    component: ComponentCreator('/blog/tags/ai-safety', '991'),
    exact: true
  },
  {
    path: '/blog/tags/announcements',
    component: ComponentCreator('/blog/tags/announcements', '0d4'),
    exact: true
  },
  {
    path: '/blog/tags/engineering',
    component: ComponentCreator('/blog/tags/engineering', '0a9'),
    exact: true
  },
  {
    path: '/blog/tags/research',
    component: ComponentCreator('/blog/tags/research', 'd3b'),
    exact: true
  },
  {
    path: '/blog/tags/verification',
    component: ComponentCreator('/blog/tags/verification', 'db5'),
    exact: true
  },
  {
    path: '/blog/trillion-dollar-risk-unverified-ai',
    component: ComponentCreator('/blog/trillion-dollar-risk-unverified-ai', '34b'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/search',
    component: ComponentCreator('/search', '5de'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '372'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'efa'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'fb7'),
            routes: [
              {
                path: '/docs',
                component: ComponentCreator('/docs', '3b3'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/advanced/agent-verification',
                component: ComponentCreator('/docs/advanced/agent-verification', '8b3'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/advanced/architecture-diagrams',
                component: ComponentCreator('/docs/advanced/architecture-diagrams', 'cf3'),
                exact: true
              },
              {
                path: '/docs/advanced/attestations',
                component: ComponentCreator('/docs/advanced/attestations', 'e1a'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/advanced/self-hosting',
                component: ComponentCreator('/docs/advanced/self-hosting', '080'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/api/authentication',
                component: ComponentCreator('/docs/api/authentication', '8fd'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/api/dsl-reference',
                component: ComponentCreator('/docs/api/dsl-reference', '859'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/api/endpoints',
                component: ComponentCreator('/docs/api/endpoints', '23f'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/api/errors',
                component: ComponentCreator('/docs/api/errors', 'b52'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/api/overview',
                component: ComponentCreator('/docs/api/overview', 'e02'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/api/rate-limits',
                component: ComponentCreator('/docs/api/rate-limits', '73b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/engines/code',
                component: ComponentCreator('/docs/engines/code', '27b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/engines/consensus',
                component: ComponentCreator('/docs/engines/consensus', '79c'),
                exact: true
              },
              {
                path: '/docs/engines/fact',
                component: ComponentCreator('/docs/engines/fact', '26c'),
                exact: true
              },
              {
                path: '/docs/engines/image',
                component: ComponentCreator('/docs/engines/image', '625'),
                exact: true
              },
              {
                path: '/docs/engines/logic',
                component: ComponentCreator('/docs/engines/logic', '055'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/engines/math',
                component: ComponentCreator('/docs/engines/math', '02b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/engines/overview',
                component: ComponentCreator('/docs/engines/overview', 'cea'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/engines/reasoning',
                component: ComponentCreator('/docs/engines/reasoning', '1d3'),
                exact: true
              },
              {
                path: '/docs/engines/sql',
                component: ComponentCreator('/docs/engines/sql', 'a9e'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/engines/stats',
                component: ComponentCreator('/docs/engines/stats', '210'),
                exact: true
              },
              {
                path: '/docs/getting-started/concepts',
                component: ComponentCreator('/docs/getting-started/concepts', '831'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/getting-started/installation',
                component: ComponentCreator('/docs/getting-started/installation', 'f1f'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/getting-started/llm-configuration',
                component: ComponentCreator('/docs/getting-started/llm-configuration', 'b71'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/getting-started/quickstart',
                component: ComponentCreator('/docs/getting-started/quickstart', 'dd9'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/integrations/crewai',
                component: ComponentCreator('/docs/integrations/crewai', 'c79'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/integrations/langchain',
                component: ComponentCreator('/docs/integrations/langchain', '3c7'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/integrations/llamaindex',
                component: ComponentCreator('/docs/integrations/llamaindex', '6ca'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/sdks/go',
                component: ComponentCreator('/docs/sdks/go', '96d'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/sdks/overview',
                component: ComponentCreator('/docs/sdks/overview', 'd3d'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/sdks/python',
                component: ComponentCreator('/docs/sdks/python', '053'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/sdks/rust',
                component: ComponentCreator('/docs/sdks/rust', '107'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/sdks/typescript',
                component: ComponentCreator('/docs/sdks/typescript', 'a1e'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/specs/agent',
                component: ComponentCreator('/docs/specs/agent', '41c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/specs/attestation',
                component: ComponentCreator('/docs/specs/attestation', '81d'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/specs/overview',
                component: ComponentCreator('/docs/specs/overview', '60c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/docs/specs/qwed-spec',
                component: ComponentCreator('/docs/specs/qwed-spec', '9c8'),
                exact: true,
                sidebar: "docsSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
