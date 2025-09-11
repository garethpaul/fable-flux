import Link from "next/link";
import Image from "next/image";

export default function TechnicalDetailsPage() {
  return (
    <div
      style={{ backgroundColor: "#DFC1B6" }}
      className="min-h-screen py-8 px-4"
    >
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block mb-6">
            <Image
              src="/fable_flux_logo.svg"
              alt="Fable Flux"
              width={120}
              height={40}
              className="hover:scale-105 transition-transform duration-200"
            />
          </Link>
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Technical Details
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            How Fable Flux generates personalized children&apos;s stories using
            AI
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          {/* Model Architecture Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <Image
                src="/openai.png"
                alt="OpenAI"
                width={32}
                height={32}
                className="mr-3"
              />
              Model Architecture
            </h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 mb-4">
                Fable Flux is powered by a fine-tuned version of OpenAI&apos;s
                GPT-OSS-20B model, specifically optimized for generating
                high-quality children&apos;s stories with educational value and
                age-appropriate content.
              </p>

              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                Model Pipeline
              </h3>
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <ol className="list-decimal list-inside text-gray-700 space-y-2">
                  <li>
                    <strong>Base Model:</strong>{" "}
                    <a
                      href="https://huggingface.co/openai/gpt-oss-20b"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      OpenAI GPT-OSS-20B
                    </a>
                  </li>
                  <li>
                    <strong>Training Dataset:</strong>{" "}
                    <a
                      href="https://huggingface.co/datasets/garethpaul/children-stories-dataset"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      Children Stories Dataset
                    </a>
                  </li>
                  <li>
                    <strong>Fine-tuning Method:</strong>{" "}
                    <a
                      href="https://huggingface.co/garethpaul/gpt-oss-20b-children-qlora"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      QLoRA (Quantized Low-Rank Adaptation)
                    </a>
                  </li>
                  <li>
                    <strong>Final Model:</strong>{" "}
                    <a
                      href="https://huggingface.co/garethpaul/gpt-oss-20b-fableflux-mxfp4"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      Fable Flux Fine-tuned Model
                    </a>
                  </li>
                </ol>
              </div>
            </div>
          </section>

          {/* Dataset Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Training Dataset
            </h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 mb-4">
                The model was trained on a carefully curated dataset of
                children&apos;s stories designed to ensure:
              </p>
              <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
                <li>Age-appropriate language (3+ years)</li>
                <li>Positive moral lessons and educational value</li>
                <li>Diverse characters, settings, and themes</li>
                <li>Engaging storytelling with clear narrative structure</li>
                <li>Safe and encouraging content</li>
              </ul>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 mb-2">
                  Dataset Highlights:
                </h4>
                <ul className="text-blue-700 space-y-1">
                  <li>• 10,000+ high-quality children&apos;s stories</li>
                  <li>• 200 diverse character archetypes</li>
                  <li>• 100 varied settings and environments</li>
                  <li>• Systematic diversity tracking</li>
                  <li>• Quality validation and sentiment analysis</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Serving Infrastructure Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Serving Infrastructure
            </h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 mb-4">
                Fable Flux uses a modern, scalable infrastructure to deliver
                fast and reliable story generation:
              </p>

              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                Technology Stack
              </h3>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    🚀 vLLM Engine
                  </h4>
                  <p className="text-gray-700 text-sm">
                    High-performance inference engine optimized for large
                    language models, providing fast token generation and
                    efficient memory usage.
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    ☁️ Modal.com Platform
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Serverless compute platform that automatically scales GPU
                    resources based on demand, ensuring optimal performance and
                    cost efficiency.
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    🎯 H100 GPUs
                  </h4>
                  <p className="text-gray-700 text-sm">
                    NVIDIA H100 Tensor Core GPUs provide the computational power
                    for real-time story generation with minimal latency.
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    ⚡ Next.js Frontend
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Modern React framework with server-side rendering, optimized
                    for performance and user experience.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Performance & Quality Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Performance & Quality
            </h2>
            <div className="prose prose-lg max-w-none">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600 mb-2">
                    ~10s
                  </div>
                  <div className="text-gray-700">Average Generation Time</div>
                </div>
                <div className="text-center bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600 mb-2">
                    600-700
                  </div>
                  <div className="text-gray-700">Words per Story</div>
                </div>
                <div className="text-center bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600 mb-2">
                    3+
                  </div>
                  <div className="text-gray-700">Target Age Range</div>
                </div>
              </div>
            </div>
          </section>

          {/* Quality Assurance Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Quality Assurance
            </h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 mb-4">
                Every generated story undergoes automated quality validation:
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <ul className="text-yellow-800 space-y-2">
                  <li>
                    ✓ <strong>Content Safety:</strong> Automated filtering for
                    age-appropriate content
                  </li>
                  <li>
                    ✓ <strong>Educational Value:</strong> Verification of
                    positive moral lessons
                  </li>
                  <li>
                    ✓ <strong>Language Complexity:</strong> Reading level
                    analysis for target age group
                  </li>
                  <li>
                    ✓ <strong>Narrative Structure:</strong> Proper story format
                    with clear beginning, middle, and end
                  </li>
                  <li>
                    ✓ <strong>Character Consistency:</strong> Logical character
                    development and behavior
                  </li>
                </ul>
              </div>
            </div>
          </section>

          {/* Technical Specifications */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Technical Specifications
            </h2>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Model Details
                  </h4>
                  <ul className="text-gray-700 space-y-1">
                    <li>• Parameters: 20 billion</li>
                    <li>• Architecture: Transformer-based</li>
                    <li>• Precision: Mixed FP16/FP4</li>
                    <li>• Context Length: 8,192 tokens</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Infrastructure
                  </h4>
                  <ul className="text-gray-700 space-y-1">
                    <li>• GPU: NVIDIA H100 (80GB)</li>
                    <li>• Memory: Tensor parallelism</li>
                    <li>• Serving: vLLM 0.10.1+gptoss</li>
                    <li>• Platform: Modal.com serverless</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Navigation */}
        <div className="text-center">
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors duration-200"
          >
            ← Back to Fable Flux
          </Link>
        </div>
      </div>
    </div>
  );
}
