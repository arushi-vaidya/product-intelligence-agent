import { motion } from "framer-motion";
import {
  ArrowRight,
  ArrowUpRight,
  Cpu,
  GitMerge,
  Network,
  ScanSearch,
} from "lucide-react";
import { Fragment } from "react";
import { useNavigate } from "react-router-dom";

import { stages } from "./NewInvestigation";
import "./home.css";

const features = [
  {
    icon: ScanSearch,
    title: "Source Discovery",
    text: "Multi-agent research across datasheets, catalogs and distributor listings.",
  },
  {
    icon: Cpu,
    title: "Spec Extraction",
    text: "Structured technical attributes pulled from HTML & PDF evidence.",
  },
  {
    icon: GitMerge,
    title: "Conflict Resolution",
    text: "Distinguishes true contradictions from real variant differences.",
  },
  {
    icon: Network,
    title: "Knowledge Graph",
    text: "AKGP entities & relationships mapped for every product family.",
  },
];

function Home() {
  const navigate = useNavigate();

  return (
    <main className="home-page">
      <div className="home-bg">
        <div className="home-bg-glow-a" />
        <div className="home-bg-glow-b" />
        <div className="home-bg-grid" />
        <div className="home-bg-scanline" />
        <div className="home-bg-noise" />
      </div>

      <section className="hero">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="hero-content"
        >
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            {stages.length}-STAGE DFOO INVESTIGATION PIPELINE
          </div>

          <h1>
            Turn a name &amp;{" "}
            <span className="highlight">manufacturer</span>{" "}
            into product intelligence.
          </h1>

          <p className="hero-description">
            Enter a manufacturer and MPN. Our agent pipeline
            researches, validates, resolves and enriches it
            into commerce-ready specifications, variants and
            a knowledge graph.
          </p>

          <div className="hero-actions">
            <button
              className="hero-cta"
              onClick={() => navigate("/investigate")}
            >
              Start New Investigation
              <ArrowUpRight size={17} strokeWidth={2.4} />
            </button>

            <div className="hero-stats">
              <span>
                <strong>{stages.length}</strong> agents
              </span>

              <span className="hero-stats-divider" />

              <span>
                <strong>{features.length + 3}</strong> intel
                modules
              </span>

              <span className="hero-stats-divider" />

              <span>
                <strong>0</strong> setup
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.15 }}
          className="hero-network"
        >
          <div className="network-orbit orbit-one" />
          <div className="network-orbit orbit-two" />

          <div className="network-node center-node">
            PRODUCT
            <strong>iC60N C20</strong>
          </div>

          <div className="network-node node-one">SOURCE</div>
          <div className="network-node node-two">VARIANT</div>
          <div className="network-node node-three">
            EVIDENCE
          </div>
          <div className="network-node node-four">SPECS</div>
        </motion.div>
      </section>

      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="feature-strip"
      >
        {features.map((feature) => (
          <div className="feature-item" key={feature.title}>
            <div className="feature-icon">
              <feature.icon size={17} strokeWidth={2} />
            </div>

            <h3>{feature.title}</h3>
            <p>{feature.text}</p>
          </div>
        ))}
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="pipeline-strip-section"
      >
        <div className="pipeline-strip-label">THE PIPELINE</div>

        <div className="pipeline-chips">
          {stages.map((stage, index) => (
            <Fragment key={stage}>
              <div className="pipeline-chip">
                <span className="pipeline-chip-number">
                  {String(index + 1).padStart(2, "0")}
                </span>
                {stage}
              </div>

              {index !== stages.length - 1 && (
                <ArrowRight
                  className="pipeline-arrow"
                  size={13}
                />
              )}
            </Fragment>
          ))}
        </div>
      </motion.section>

      <footer className="home-footer">
        <span>
          AKGP.INTEL &mdash; INDUSTRIAL PRODUCT INTELLIGENCE
        </span>
      </footer>
    </main>
  );
}

export default Home;