'use client';

import { useState } from 'react';
import { ChevronRight, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

type Step = 'llm' | 'enrichment' | 'crm' | 'email' | 'company';

const steps: { key: Step; title: string; description: string }[] = [
  { key: 'llm', title: 'LLM Provider', description: 'Configure your AI provider' },
  { key: 'enrichment', title: 'Enrichment', description: 'Choose data enrichment source' },
  { key: 'crm', title: 'CRM Integration', description: 'Connect your CRM system' },
  { key: 'email', title: 'Email Provider', description: 'Set up email delivery' },
  { key: 'company', title: 'Company Info', description: 'Your organization details' },
];

export default function SetupWizard() {
  const [currentStep, setCurrentStep] = useState<Step>('llm');
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [isCompleted, setIsCompleted] = useState(false);

  const currentStepIndex = steps.findIndex((s) => s.key === currentStep);

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStep(steps[currentStepIndex + 1].key);
    } else {
      setIsCompleted(true);
      // In production, save to API
      console.log('Setup complete:', formData);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(steps[currentStepIndex - 1].key);
    }
  };

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (isCompleted) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white border rounded-lg p-8 text-center">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="h-8 w-8 text-emerald-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">
            Setup Complete!
          </h1>
          <p className="text-slate-600 mb-6">
            Your AI Sales Lead Qualifier is now configured and ready to use.
          </p>
          <a
            href="/"
            className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">First-Time Setup</h1>
      <p className="text-slate-600 mb-8">
        Configure your AI Sales Lead Qualifier to get started.
      </p>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const isActive = step.key === currentStep;
            const isCompleted = steps.findIndex((s) => s.key === currentStep) > index;

            return (
              <div key={step.key} className="flex items-center">
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold',
                    isActive
                      ? 'bg-indigo-600 text-white'
                      : isCompleted
                      ? 'bg-emerald-500 text-white'
                      : 'bg-slate-200 text-slate-500'
                  )}
                >
                  {isCompleted ? <Check className="h-4 w-4" /> : index + 1}
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      'w-16 h-0.5',
                      isCompleted ? 'bg-emerald-500' : 'bg-slate-200'
                    )}
                  />
                )}
              </div>
            );
          })}
        </div>
        <div className="flex justify-between mt-2">
          {steps.map((step) => (
            <div key={step.key} className="text-xs text-slate-500 w-24 text-center">
              {step.title}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white border rounded-lg p-6">
        {currentStep === 'llm' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900">
              LLM API Configuration
            </h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Provider
              </label>
              <select
                value={formData.llmProvider || 'openai'}
                onChange={(e) => updateField('llmProvider', e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google AI</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                API Key
              </label>
              <input
                type="password"
                value={formData.llmApiKey || ''}
                onChange={(e) => updateField('llmApiKey', e.target.value)}
                placeholder="sk-..."
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
          </div>
        )}

        {currentStep === 'enrichment' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900">
              Enrichment Provider
            </h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Provider
              </label>
              <select
                value={formData.enrichmentProvider || 'mock'}
                onChange={(e) => updateField('enrichmentProvider', e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="mock">Mock (Development)</option>
                <option value="clearbit">Clearbit</option>
                <option value="apollo">Apollo</option>
              </select>
            </div>
            {formData.enrichmentProvider !== 'mock' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  API Key
                </label>
                <input
                  type="password"
                  value={formData.enrichmentApiKey || ''}
                  onChange={(e) =>
                    updateField('enrichmentApiKey', e.target.value)
                  }
                  placeholder="Enter API key"
                  className="w-full border rounded-lg px-3 py-2"
                />
              </div>
            )}
          </div>
        )}

        {currentStep === 'crm' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900">
              CRM Integration
            </h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                CRM Provider
              </label>
              <select
                value={formData.crmProvider || 'none'}
                onChange={(e) => updateField('crmProvider', e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="none">None</option>
                <option value="hubspot">HubSpot</option>
                <option value="salesforce">Salesforce</option>
                <option value="pipedrive">Pipedrive</option>
              </select>
            </div>
          </div>
        )}

        {currentStep === 'email' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900">
              Email Provider
            </h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Provider
              </label>
              <select
                value={formData.emailProvider || 'console'}
                onChange={(e) => updateField('emailProvider', e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="console">Console (Development)</option>
                <option value="smtp">SMTP</option>
                <option value="sendgrid">SendGrid</option>
              </select>
            </div>
            {formData.emailProvider === 'smtp' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    SMTP Host
                  </label>
                  <input
                    type="text"
                    value={formData.smtpHost || ''}
                    onChange={(e) => updateField('smtpHost', e.target.value)}
                    placeholder="smtp.example.com"
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    SMTP Port
                  </label>
                  <input
                    type="number"
                    value={formData.smtpPort || ''}
                    onChange={(e) => updateField('smtpPort', e.target.value)}
                    placeholder="587"
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
              </>
            )}
          </div>
        )}

        {currentStep === 'company' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-900">
              Company Information
            </h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Company Name
              </label>
              <input
                type="text"
                value={formData.companyName || ''}
                onChange={(e) => updateField('companyName', e.target.value)}
                placeholder="Acme Inc."
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Industry
              </label>
              <input
                type="text"
                value={formData.industry || ''}
                onChange={(e) => updateField('industry', e.target.value)}
                placeholder="Technology"
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6 pt-6 border-t">
          <button
            onClick={handleBack}
            disabled={currentStepIndex === 0}
            className={cn(
              'px-6 py-2 rounded-lg font-medium transition-colors',
              currentStepIndex === 0
                ? 'text-slate-300 cursor-not-allowed'
                : 'text-slate-700 hover:bg-slate-100'
            )}
          >
            Back
          </button>
          <button
            onClick={handleNext}
            className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {currentStepIndex === steps.length - 1 ? 'Complete' : 'Continue'}
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
