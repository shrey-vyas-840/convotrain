import { ChangeEvent, useRef, useState } from "react";
import {
  ArrowDownRight, ArrowRight, BadgeCheck, BarChart3, Bot, CalendarDays, Check,
  ChevronDown, ChevronRight, Clock3, FileText, Globe2, Headphones, Languages,
  LockKeyhole, Menu, Mic2, PhoneCall, Play, Plus, Rocket, Send, ShieldCheck,
  Sparkles, Store, UploadCloud, Users, Volume2, X, Zap
} from "lucide-react";

type Page = "home" | "auth";
type AuthMode = "login" | "signup";

const faq = [
  ["What does ConvoTrain learn?", "Business facts such as opening hours, menu items, prices, offers, delivery rules, reservation policies, holidays and special instructions."],
  ["Does it train the LLM?", "No. The MVP stores each restaurant's structured knowledge and uses retrieval to ground the response. The base model stays shared."],
  ["Can customers speak to it?", "Yes. Browser voice is part of the MVP. Real phone-call automation is planned for a later phase."],
  ["Can I update information later?", "Yes. Facts can be reviewed, edited, replaced, deleted and versioned so changing business information can be reflected quickly."],
  ["Which languages are supported?", "English, Hindi and Gujarati are the initial target languages, with cross-language retrieval in the architecture."],
];

const testimonials = [
  { name: "Aarav Patel", role: "Sample Restaurant Owner", quote: "We stopped repeating the same opening-hours and menu answers all day. The assistant feels like a trained front-desk teammate." },
  { name: "Meera Shah", role: "Sample Cafe Manager", quote: "The best part is how easy it is to update. I can teach a new offer in plain language instead of editing prompts." },
  { name: "Rohan Mehta", role: "Sample QSR Operator", quote: "For a busy lunch window, even simple questions add up. ConvoTrain turns those repetitive conversations into an automated workflow." },
];

const capabilities = [
  [PhoneCall, "Customer conversations", "Handle common restaurant questions with the same business context every time."],
  [FileText, "Knowledge extraction", "Turn free-form owner input into structured, searchable facts."],
  [Languages, "Indian-language ready", "English, Hindi and Gujarati first, with cross-language retrieval built into the design."],
  [ShieldCheck, "Tenant-isolated", "Each restaurant gets a private knowledge space, sessions, settings and conversation history."],
];

export function App() {
  const [page, setPage] = useState<Page>("home");
  const [authMode, setAuthMode] = useState<AuthMode>("signup");
  const [menuOpen, setMenuOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [showDemo, setShowDemo] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const goHome = () => {
    setPage("home");
    setMenuOpen(false);
    requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  };

  const scrollTo = (id: string) => {
    setPage("home");
    setMenuOpen(false);
    requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }));
  };

  const openAuth = (mode: AuthMode) => {
    setAuthMode(mode);
    setPage("auth");
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] ?? null);
  const triggerUpload = () => fileInputRef.current?.click();

  if (page === "auth") {
    return (
      <div className="auth-page">
        <div className="noise" />
        <div className="auth-shell">
          <button className="brand auth-brand" onClick={goHome}><span className="brand-mark"><Zap size={17}/></span>ConvoTrain</button>
          <div className="auth-layout">
            <div className="auth-intro">
              <span className="kicker"><Sparkles size={14}/> CONVERSATIONAL AI FOR RESTAURANTS</span>
              <h1>Turn your business knowledge into an <em>always-on</em> AI front desk.</h1>
              <p>Teach hours, menu, pricing, offers, holidays and delivery rules in everyday language. ConvoTrain structures the facts and uses them to answer customer questions.</p>
              <div className="auth-checks">
                {["No prompt engineering", "Reviewable knowledge", "English · Hindi · Gujarati", "Browser voice in the MVP"].map((x)=><span key={x}><Check size={15}/>{x}</span>)}
              </div>
            </div>
            <div className="auth-card">
              <div className="auth-tabs"><button className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>Log in</button><button className={authMode === "signup" ? "active" : ""} onClick={() => setAuthMode("signup")}>Create account</button></div>
              <span className="auth-tag">{authMode === "login" ? "WELCOME BACK" : "START YOUR WORKSPACE"}</span>
              <h2>{authMode === "login" ? "Continue where you left off." : "Build your restaurant AI."}</h2>
              <p className="auth-sub">{authMode === "login" ? "Open your workspace and review your AI knowledge." : "Create a private restaurant knowledge space in a few steps."}</p>
              {authMode === "signup" && <label>Restaurant name<input placeholder="e.g. Green Fork" /></label>}
              <label>Email<input type="email" placeholder="you@restaurant.com" /></label>
              <label>Password<input type="password" placeholder="••••••••" /></label>
              {authMode === "signup" && <label>Preferred language<select defaultValue="English"><option>English</option><option>Hindi</option><option>Gujarati</option></select></label>}
              <button className="auth-submit" onClick={() => alert("Demo UI submitted. Connect to /auth/signup or /auth/login when your backend is ready.")}>{authMode === "login" ? "Log in" : "Create account"}<ArrowRight size={16}/></button>
              <small>Demo UI only — connect to the FastAPI auth APIs when the backend is live.</small>
              <button className="back-link" onClick={goHome}>← Back to ConvoTrain</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="site">
      <header className="topbar">
        <div className="container nav">
          <button className="brand" onClick={goHome}><span className="brand-mark"><Zap size={17}/></span>ConvoTrain</button>
          <div className={`nav-links ${menuOpen ? "open" : ""}`}>
            <button onClick={() => scrollTo("product")}>Product</button>
            <button onClick={() => scrollTo("capabilities")}>Capabilities</button>
            <button onClick={() => scrollTo("results")}>Results</button>
            <button onClick={() => scrollTo("faq")}>FAQ</button>
            <button className="mobile-login" onClick={() => openAuth("login")}>Log in</button>
            <button className="mobile-upload" onClick={triggerUpload}><UploadCloud size={14}/> Upload data</button>
          </div>
          <div className="nav-actions"><button onClick={() => openAuth("login")}>Log in</button><button className="upload-action" onClick={triggerUpload}><UploadCloud size={15}/> Upload data</button></div>
          <button className="menu" onClick={() => setMenuOpen(v=>!v)}>{menuOpen ? <X/> : <Menu/>}</button>
        </div>
      </header>

      <input className="hidden-file" ref={fileInputRef} type="file" onChange={onFileChange}/>

      <main>
        <section className="new-hero" id="product">
          <div className="new-hero-bg" />
          <div className="container hero-layout">
            <div className="hero-left">
              <span className="kicker"><Sparkles size={14}/> RESTAURANT VOICE + KNOWLEDGE AI</span>
              <h1>Give your restaurant an <span>AI front desk.</span></h1>
              <p>Teach ConvoTrain what your business knows. Then let an AI agent handle repetitive customer conversations using your private, structured restaurant knowledge.</p>
              <div className="hero-buttons"><button className="primary" onClick={() => openAuth("signup")}>Build my AI agent <ArrowRight size={17}/></button><button className="secondary" onClick={() => setShowDemo(true)}><Play size={15}/> See a live example</button></div>
              <div className="micro-proof"><span><BadgeCheck size={14}/> Private knowledge per restaurant</span><span><Languages size={14}/> English · Hindi · Gujarati</span><span><Clock3 size={14}/> Near real-time responses</span></div>
            </div>

            <div className="call-demo-card">
              <div className="call-top"><div className="live-pill"><i/> Live demo</div><span>ConvoTrain AI</span></div>
              <div className="call-center"><div className="wave-wrap"><div className="voice-orb"><Bot size={42}/></div>{Array.from({length:12}).map((_,i)=><span className="wave-bar" key={i} style={{height: `${18 + (i%4)*9}px`}} />)}</div><strong>AI receptionist</strong><span>Listening · EN</span></div>
              <div className="call-bubble customer"><small>Customer</small>Are you open tomorrow? And do you still have the paneer pizza?</div>
              <div className="call-bubble agent"><small>ConvoTrain</small>Yes. We open at 11 AM tomorrow, and Paneer Pizza is available for ₹250.</div>
              <div className="call-meta"><span><ShieldCheck size={14}/> Answer grounded in restaurant knowledge</span><span><Volume2 size={14}/> Voice-ready</span></div>
            </div>
          </div>
          <div className="container logo-row"><span>BUILT FOR BUSY RESTAURANTS</span><div><b><Store size={14}/> GREEN FORK</b><b><Store size={14}/> URBAN THALI</b><b><Store size={14}/> CAFE 24</b><b><Store size={14}/> BOWL HOUSE</b></div></div>
        </section>

        <section className="section dark-section" id="capabilities">
          <div className="container">
            <div className="section-top"><div><span className="kicker muted"><Sparkles size={14}/> WHY CONVOTRAIN</span><h2>One AI layer for the conversations your team answers all day.</h2></div><p>Built around the business-specific knowledge problem: capture it, structure it, retrieve it, then respond.</p></div>
            <div className="cap-grid">{capabilities.map(([Icon,title,text],i)=><article key={title as string} className="cap-card"><div className="cap-number">0{i+1}</div><div className="cap-icon"><Icon size={21}/></div><h3>{title as string}</h3><p>{text as string}</p><button onClick={() => scrollTo("how")}>Explore <ArrowRight size={14}/></button></article>)}</div>
          </div>
        </section>

        <section className="section light-section" id="how">
          <div className="container">
            <div className="center-head"><span className="kicker purple"><Rocket size={14}/> FROM KNOWLEDGE TO CONVERSATION</span><h2>Train it once. Keep it current.</h2><p>The owner experience is deliberately simple: talk to the system like you are training a new employee.</p></div>
            <div className="process-grid">
              <div className="process-card"><span>01</span><Mic2 size={20}/><h3>Teach</h3><p>Type or speak business details in natural language.</p><div className="mini-chat"><b>Owner</b><p>“Sunday is closed. Free delivery within 5 km.”</p></div></div>
              <div className="process-card"><span>02</span><BarChart3 size={20}/><h3>Structure</h3><p>Facts are extracted into categories such as hours, menu, offers and policies.</p><div className="fact-stack"><i>business_hours</i><i>delivery_rule</i><i>offer</i></div></div>
              <div className="process-card"><span>03</span><ShieldCheck size={20}/><h3>Review</h3><p>Owners can approve, edit, delete and version the knowledge before it becomes active.</p><div className="review-line"><Check size={13}/> Sunday · closed <strong>Approved</strong></div></div>
              <div className="process-card"><span>04</span><PhoneCall size={20}/><h3>Answer</h3><p>Customer questions are answered from the latest restaurant-specific context.</p><div className="answer-line"><small>Customer</small><strong>“Do you deliver nearby?”</strong><span>Yes — within 5 km.</span></div></div>
            </div>
          </div>
        </section>

        <section className="section black-section">
          <div className="container split-feature">
            <div className="knowledge-art">
              <div className="knowledge-window"><div className="window-bar"><span>Restaurant knowledge</span><i/></div><div className="window-row big"><div className="fact-avatar">H</div><div><small>Business hours</small><strong>Mon–Sat · 11:00 AM — 11:00 PM</strong></div><b>v24</b></div><div className="window-row"><div className="fact-dot purple-dot"/><div><small>Menu item</small><strong>Paneer Pizza · ₹250 · available</strong></div><b>active</b></div><div className="window-row"><div className="fact-dot green-dot"/><div><small>Delivery rule</small><strong>Free delivery · 5 km radius</strong></div><b>active</b></div><div className="window-row"><div className="fact-dot orange-dot"/><div><small>Offer</small><strong>Birthday discount · 20%</strong></div><b>new</b></div></div>
              <div className="floating-chip chip-one"><Check size={14}/> Approved fact</div><div className="floating-chip chip-two"><LockKeyhole size={14}/> Tenant scoped</div>
            </div>
            <div className="split-copy"><span className="kicker muted">THE BUSINESS BRAIN</span><h2>Your restaurant's facts are the product.</h2><p>ConvoTrain is not positioned as a generic chatbot builder. Its core asset is a structured private knowledge base that can evolve as your restaurant changes.</p><div className="bullets"><span><Check size={15}/> PostgreSQL for exact business facts</span><span><Check size={15}/> Qdrant for semantic retrieval</span><span><Check size={15}/> Versioned updates and conflict review</span><span><Check size={15}/> Tenant-scoped retrieval to prevent data mixing</span></div><button className="secondary dark-cta" onClick={() => openAuth("signup")}>Create a knowledge workspace <ArrowRight size={16}/></button></div>
          </div>
        </section>

        <section className="section light-section" id="results">
          <div className="container">
            <div className="section-top light-top"><div><span className="kicker purple"><BarChart3 size={14}/> IMPACT / DEMO MODE</span><h2>See the kind of workflow ConvoTrain is built to unlock.</h2></div><p>These numbers are <strong>illustrative demo metrics</strong>, not live customer results. Replace them with measured product data as pilots go live.</p></div>
            <div className="metric-banners"><div><small>Illustrative response time</small><strong>&lt; 2s</strong><span>for typical text interactions</span></div><div><small>Illustrative knowledge coverage</small><strong>90%+</strong><span>of repetitive FAQ-style queries</span></div><div><small>Illustrative staff time recovered</small><strong>8–12 hrs</strong><span>per week for a busy location</span></div><div><small>Languages in MVP</small><strong>3</strong><span>English · Hindi · Gujarati</span></div></div>
            <div className="roi-card"><div><span className="kicker purple">MISSED-CONVERSATION EFFECT</span><h3>What happens when every repetitive question gets an instant answer?</h3><p>Use this section later with real pilot data: unanswered calls, response time, staff hours, order conversion and knowledge-update turnaround.</p></div><div className="roi-graphic"><div className="roi-bars"><span style={{height:"42%"}}/><span style={{height:"60%"}}/><span style={{height:"76%"}}/><span style={{height:"92%"}}/></div><div className="roi-labels"><i>Before</i><i>After</i></div></div></div>

            <div className="review-head"><div><span className="kicker purple"><Users size={14}/> CUSTOMER VOICE</span><h2>Sample feedback from restaurant pilots.</h2></div><span className="demo-badge">ILLUSTRATIVE / PLACEHOLDER</span></div>
            <div className="review-grid">{testimonials.map(t=><article key={t.name}><div className="stars">★★★★★</div><p>“{t.quote}”</p><div><strong>{t.name}</strong><span>{t.role}</span></div></article>)}</div>
          </div>
        </section>

        <section className="section dark-section launch-section">
          <div className="container"><div className="section-top"><div><span className="kicker muted"><Rocket size={14}/> LAUNCH PATH</span><h2>From one restaurant to a scalable multi-tenant platform.</h2></div><p>Start simple, validate the knowledge loop, then add production voice automation and broader scale.</p></div><div className="roadmap"><div><span>01</span><b>Onboard</b><small>Restaurant + owner</small></div><ArrowRight/><div><span>02</span><b>Teach</b><small>Knowledge capture</small></div><ArrowRight/><div><span>03</span><b>Answer</b><small>Text + browser voice</small></div><ArrowRight/><div><span>04</span><b>Scale</b><small>Phone + more channels</small></div></div></div>
        </section>

        <section className="section light-section" id="faq">
          <div className="container faq-wrap"><div className="center-head"><span className="kicker purple">FAQ</span><h2>Questions owners usually ask.</h2></div><div className="faq-list">{faq.map(([q,a],i)=><div key={q} className={openFaq===i ? "faq open" : "faq"}><button onClick={()=>setOpenFaq(openFaq===i?null:i)}><span>{q}</span>{openFaq===i ? <X size={18}/> : <Plus size={18}/>}</button>{openFaq===i && <p>{a}</p>}</div>)}</div></div>
        </section>

        <section className="cta-band"><div className="container cta-inner"><div><span className="kicker muted">READY TO BUILD?</span><h2>Give your restaurant a conversational AI layer.</h2><p>Upload your business information, create a workspace and start building your restaurant knowledge base.</p></div><div className="cta-actions"><button className="primary" onClick={() => openAuth("signup")}>Start building <ArrowRight size={17}/></button><button className="secondary" onClick={triggerUpload}><UploadCloud size={16}/> Upload data</button></div></div></section>
      </main>

      <footer className="footer"><div className="container footer-main"><div className="footer-brand"><button className="brand" onClick={goHome}><span className="brand-mark"><Zap size={17}/></span>ConvoTrain</button><p>Restaurant-first conversational AI built around private business knowledge.</p></div><div><h4>Product</h4><button onClick={()=>scrollTo("product")}>Overview</button><button onClick={()=>scrollTo("capabilities")}>Capabilities</button><button onClick={()=>scrollTo("results")}>Results</button><button onClick={()=>scrollTo("faq")}>FAQ</button></div><div><h4>Platform</h4><span>Knowledge extraction</span><span>Hybrid retrieval</span><span>Browser voice</span><span>Tenant isolation</span></div><div><h4>Get started</h4><button onClick={()=>openAuth("signup")}>Create account</button><button onClick={()=>openAuth("login")}>Log in</button><button onClick={triggerUpload}>Upload data</button></div><div><h4>Built on</h4><span>FastAPI</span><span>PostgreSQL</span><span>Qdrant</span><span>Open-source models</span></div></div><div className="container footer-bottom"><span>© 2026 ConvoTrain · Product prototype</span><span>Illustrative testimonials and demo metrics are marked where used.</span></div></footer>

      {file && <div className="upload-toast"><UploadCloud size={16}/><div><strong>{file.name}</strong><span>{Math.max(1,Math.round(file.size/1024))} KB · selected for upload</span></div><button onClick={()=>setFile(null)}><X size={15}/></button></div>}
      {showDemo && <div className="demo-overlay" onClick={()=>setShowDemo(false)}><div className="demo-box" onClick={(e)=>e.stopPropagation()}><button className="demo-close" onClick={()=>setShowDemo(false)}><X size={18}/></button><span className="kicker purple">LIVE PRODUCT EXAMPLE</span><h2>A customer asks. The AI answers from the latest approved fact.</h2><div className="demo-chat"><div className="demo-msg customer-msg"><small>Customer · Hindi</small>Kal kab khulega?</div><div className="demo-msg agent-msg"><small>ConvoTrain</small>We open at 11 AM tomorrow. Sunday is closed.</div><div className="demo-source"><ShieldCheck size={15}/> Source: approved business_hours fact · v24</div></div><button className="primary" onClick={()=>{setShowDemo(false);openAuth("signup")}}>Build this for my restaurant <ArrowRight size={16}/></button></div></div>}
    </div>
  );
}
