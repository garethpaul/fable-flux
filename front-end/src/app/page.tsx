"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import StoryModal from "@/components/StoryModal";

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#DFC1B6" }}>
      <div className="container mx-auto px-4 py-8">
        <div className="text-center max-w-4xl mx-auto">
          {/* Fable Flux Logo */}
          <div className="mb-6">
            <Image
              src="/fable_flux_logo.svg"
              alt="Fable Flux Logo"
              width={710}
              height={565}
              className="mx-auto max-w-48 w-full h-auto"
            />
          </div>

          {/* Hero Text */}
          <div className="mb-6">
            <Image
              src="/hero_text.svg"
              alt="Personalized Storytelling Unforgettable Lessons"
              width={976}
              height={163}
              className="mx-auto max-w-lg w-full h-auto"
            />
          </div>

          {/* Hero Image */}
          <div className="mb-8">
            <Image
              src="/fable_flux_hero.png"
              alt="Fable Flux Hero"
              width={1212}
              height={1046}
              className="mx-auto max-w-xl w-full h-auto"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            {/* Create Story Button */}
            <button
              onClick={() => setIsModalOpen(true)}
              className="transition-transform hover:scale-105 focus:outline-none"
            >
              <Image
                src="/create_story.svg"
                alt="Create Story"
                width={1391}
                height={146}
                className="max-w-sm w-full h-auto"
              />
            </button>

            {/* Learn More Button */}
            <Link
              href="/technical-details"
              className="transition-transform hover:scale-105 focus:outline-none"
            >
              <Image
                src="/learn_more_btn.png"
                alt="Learn More"
                width={1391}
                height={146}
                className="max-w-sm w-full h-auto"
              />
            </Link>
          </div>
        </div>
      </div>

      {/* Story Modal */}
      <StoryModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
