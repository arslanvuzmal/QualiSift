'use client';

import { useState } from 'react';
import { ChevronRight, ChevronLeft, Check, Sparkles, Building, Key, Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';

type Step = 'llm' | 'enrichment' | 'crm' | 'company';

const steps: { key: Step; title: string; description: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: 'llm', title: 'AI Provider', description: 'Configure language model', icon: Sparkles },
  { key: 'enrichment', title: 'Data Enrichment', description: 'Connect data sources', icon: Database },
  { key: 'crm', title: 'Integrations', description: 'Connect your CRM', icon: Key },
  { key: 'company', title: 'Organization', description: 'Your company details', icon: Building },
];

export default function SetupWizard() {
  const router = useRouter();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [formData, setFormData] = useState<Record<string, string>>({
    llmProvider: 'openai',
    enrichmentProvider: 'mock',
    crmProvider: 'none',
  });
  const [isCompleted, setIsCompleted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentStep = steps[currentStepIndex];

  const handleNext = async () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
    } else {
      setIsSubmitting(true);
      // Simulate API call
      setTimeout(() => {
        setIsSubmitting(false);
        setIsCompleted(true);
      }, 1500);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (isCompleted) {
    return (
      <div className="max-w-2xl mx-auto py-20 animate-in fade-in zoom-in duration-500">
        <div className="enterprise-card bg-slate-900 border-slate-800 p-12 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-emerald-400 to-emerald-600" />
          <div className="mx-auto w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mb-6 border border-emerald-500/20">
            <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center">
              <Check className="h-8 w-8 text-emerald-400" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-slate-100 mb-3 tracking-tight">
            You're all set!
          </h1>
          <p className="text-slate-400 mb-8 max-w-sm mx-auto text-lg">
            QualiSift is fully configured and ready to start qualifying your pipeline.
          </p>
          <button
            onClick={() => router.push('/')}
            className="btn-primary py-3 px-8 text-base shadow-[0_0_20px_rgba(79,70,229,0.3)]"
          >
            Go to Dashboard <ChevronRight className="h-5 w-5 ml-2" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto pb-24">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">Workspace Setup</h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure your AI engine and integrations.
        </p>
      </div>

      {/* Modern Progress Bar */}
      <div className="mb-10 relative">
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded-full bg-slate-800">
          <div 
            style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }} 
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)] transition-all duration-500" 
          />
        </div>
        <div className="flex justify-between">
          {steps.map((step, idx) => {
            const isPast = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;
            return (
              <div key={step.key} className="flex flex-col items-center w-1/4">
                <div className={cn(
                  "flex items-center justify-center w-10 h-10 rounded-full mb-2 transition-colors duration-300",
                  isPast ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30" :
                  isCurrent ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]" :
                  "bg-slate-800 text-slate-500 border border-slate-700"
                )}>
                  {isPast ? <Check className="h-5 w-5" /> : <step.icon className="h-4 w-4" />}
                </div>
                <span className={cn(
                  "text-xs font-semibold uppercase tracking-wider text-center mt-1",
                  isCurrent ? "text-indigo-400" : isPast ? "text-slate-300" : "text-slate-500"
                )}>
                  {step.title}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Form Content Wrapper with transition container */}
      <div className="enterprise-card relative overflow-hidden bg-slate-900 border-slate-800 min-h-[400px] flex flex-col">
        <div className="p-8 flex-1">
          
          {currentStep.key === 'llm' && (
            <div className="space-y-6 animate-in slide-in-from-right-4 fade-in duration-300">
              <div>
                <h2 className="text-xl font-bold text-slate-100">AI Provider Configuration</h2>
                <p className="text-sm text-slate-400 mt-1">Select the language model that will power your lead scoring.</p>
              </div>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                    Provider
                  </label>
                  <select
                    value={formData.llmProvider}
                    onChange={(e) => updateField('llmProvider', e.target.value)}
                    className="w-full border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none"
                  >
                    <option value="openai">OpenAI (Recommended)</option>
                    <option value="anthropic">Anthropic Claude</option>
                    <option value="google">Google Gemini</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={formData.llmApiKey || ''}
                    onChange={(e) => updateField('llmApiKey', e.target.value)}
                    placeholder="sk-..."
                    className="w-full border border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none placeholder:text-slate-500"
                  />
                  <p className="text-xs text-slate-500 mt-2">Your key is encrypted and stored securely.</p>
                </div>
              </div>
            </div>
          )}

          {currentStep.key === 'enrichment' && (
            <div className="space-y-6 animate-in slide-in-from-right-4 fade-in duration-300">
              <div>
                <h2 className="text-xl font-bold text-slate-100">Data Enrichment</h2>
                <p className="text-sm text-slate-400 mt-1">Automatically pull firmographics and contact details.</p>
              </div>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                    Data Source
                  </label>
                  <select
                    value={formData.enrichmentProvider}
                    onChange={(e) => updateField('enrichmentProvider', e.target.value)}
                    className="w-full border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none"
                  >
                    <option value="mock">Mock Data (Development)</option>
                    <option value="clearbit">Clearbit</option>
                    <option value="apollo">Apollo.io</option>
                  </select>
                </div>
                {formData.enrichmentProvider !== 'mock' && (
                  <div className="animate-in fade-in slide-in-from-top-2">
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                      Enrichment API Key
                    </label>
                    <input
                      type="password"
                      value={formData.enrichmentApiKey || ''}
                      onChange={(e) => updateField('enrichmentApiKey', e.target.value)}
                      placeholder="Enter API key"
                      className="w-full border border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none placeholder:text-slate-500"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep.key === 'crm' && (
            <div className="space-y-6 animate-in slide-in-from-right-4 fade-in duration-300">
              <div>
                <h2 className="text-xl font-bold text-slate-100">CRM Integration</h2>
                <p className="text-sm text-slate-400 mt-1">Sync scored leads directly to your CRM.</p>
              </div>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                    CRM Platform
                  </label>
                  <select
                    value={formData.crmProvider}
                    onChange={(e) => updateField('crmProvider', e.target.value)}
                    className="w-full border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none"
                  >
                    <option value="none">Skip for now</option>
                    <option value="hubspot">HubSpot</option>
                    <option value="salesforce">Salesforce</option>
                  </select>
                </div>
                
                {formData.crmProvider !== 'none' && (
                  <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 animate-in fade-in slide-in-from-top-2">
                    <p className="text-sm text-amber-400 font-medium">
                      You will be redirected to authenticate with {formData.crmProvider === 'hubspot' ? 'HubSpot' : 'Salesforce'} after completing setup.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep.key === 'company' && (
            <div className="space-y-6 animate-in slide-in-from-right-4 fade-in duration-300">
              <div>
                <h2 className="text-xl font-bold text-slate-100">Company Information</h2>
                <p className="text-sm text-slate-400 mt-1">Personalize the dashboard for your team.</p>
              </div>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                    Workspace Name
                  </label>
                  <input
                    type="text"
                    value={formData.companyName || ''}
                    onChange={(e) => updateField('companyName', e.target.value)}
                    placeholder="Acme Corp"
                    className="w-full border border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none placeholder:text-slate-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1.5">
                    Industry / Vertical
                  </label>
                  <input
                    type="text"
                    value={formData.industry || ''}
                    onChange={(e) => updateField('industry', e.target.value)}
                    placeholder="B2B SaaS"
                    className="w-full border border-slate-700 rounded-lg bg-slate-800 px-4 py-2.5 text-sm text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow outline-none placeholder:text-slate-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="bg-slate-900/50 p-4 border-t border-slate-800 flex items-center justify-between rounded-b-xl">
          <button
            onClick={handleBack}
            disabled={currentStepIndex === 0 || isSubmitting}
            className={cn(
              'btn-secondary flex items-center gap-1.5',
              currentStepIndex === 0 ? 'opacity-0 pointer-events-none' : ''
            )}
          >
            <ChevronLeft className="h-4 w-4" /> Back
          </button>
          
          <button
            onClick={handleNext}
            disabled={isSubmitting}
            className="btn-primary flex items-center gap-1.5"
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </span>
            ) : (
              <>
                {currentStepIndex === steps.length - 1 ? 'Complete Setup' : 'Continue'}
                {currentStepIndex !== steps.length - 1 && <ChevronRight className="h-4 w-4" />}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
