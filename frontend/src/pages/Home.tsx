import { motion } from "framer-motion";
import { ArrowRight, History, Plus, Network } from "lucide-react";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <main className="home-page">
      <div className="home-grid" />

      <section className="hero">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="hero-content"
        >
          <div className="eyebrow">
            <Network size={14} />
            INDUSTRIAL INTELLIGENCE ENGINE
          </div>

          <h1>
            From fragmented data
            <br />
            to <span>product truth.</span>
          </h1>

          <p>
            Research, validate, resolve and enrich industrial
            product information into structured, commerce-ready
            intelligence.
          </p>

          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={() => navigate("/investigate")}
            >
              <Plus size={18} />
              New Investigation
              <ArrowRight size={17} />
            </button>

            
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

          <div className="network-node node-one">
            SOURCE
          </div>

          <div className="network-node node-two">
            VARIANT
          </div>

          <div className="network-node node-three">
            EVIDENCE
          </div>

          <div className="network-node node-four">
            SPECS
          </div>
        </motion.div>
      </section>

      <section className="process-strip">
        <ProcessItem
          number="01"
          title="Research"
          text="Discover product sources"
        />

        <div className="process-line" />

        <ProcessItem
          number="02"
          title="Validate"
          text="Evaluate source evidence"
        />

        <div className="process-line" />

        <ProcessItem
          number="03"
          title="Resolve"
          text="Identify variants & conflicts"
        />

        <div className="process-line" />

        <ProcessItem
          number="04"
          title="Enrich"
          text="Generate commerce intelligence"
        />
      </section>
    </main>
  );
}

function ProcessItem({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="process-item">
      <span>{number}</span>

      <div>
        <strong>{title}</strong>
        <p>{text}</p>
      </div>
    </div>
  );
}

export default Home;