import CTA from "../components/CTA";
import Features from "../components/Features";
import HeroSection from "../components/HeroSection";
import HowItWorks from "../components/HowItWorks";
import TemplatePreview from "../components/TemplatePreview";

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-slate-900 dark:bg-gray-900 dark:text-white">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 py-10">
        <HeroSection />
        <Features />
        <HowItWorks />
        <TemplatePreview />
        <CTA />
      </div>
    </main>
  );
}
