import { useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  MessageSquare,
  Plus,
  Search,
  Settings,
  Shield,
  User,
  Building2,
  LogOut,
  Menu,
  X,
} from "lucide-react";

type AccountSection = "account" | "workspace";
type AccountSubtab =
  | "profile"
  | "security"
  | "business"
  | "preferences";

type AccountPageProps = {
  onBackHome: () => void;
};

export default function AccountPage({ onBackHome }: AccountPageProps) {
  const [openSection, setOpenSection] = useState<AccountSection>("account");
  const [activeTab, setActiveTab] = useState<AccountSubtab>("profile");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const selectTab = (section: AccountSection, tab: AccountSubtab) => {
    setOpenSection(section);
    setActiveTab(tab);
    setSidebarOpen(false);
  };

  return (
    <div className="account-page">
      <aside className={`account-sidebar ${sidebarOpen ? "mobile-open" : ""}`}>
        <div className="account-sidebar-top">
          <button
  className="account-mobile-close"
  onClick={() => setSidebarOpen(false)}
  aria-label="Close sidebar"
>
  <X size={19} />
</button>
          <button className="account-sidebar-brand" onClick={onBackHome}>
            <span className="account-brand-mark">C</span>
            <span>ConvoTrain</span>
          </button>

          <button className="account-new-chat">
            <Plus size={17} />
            <span>New conversation</span>
          </button>

          <div className="account-search">
            <Search size={16} />
            <span>Search</span>
          </div>
        </div>

        <div className="account-menu">
          {/* MAIN TAB 1 */}
          <button
            className={`account-main-tab ${
              openSection === "account" ? "open" : ""
            }`}
            onClick={() =>
              setOpenSection(
                openSection === "account" ? "workspace" : "account"
              )
            }
          >
            <span className="account-main-label">
              <User size={18} />
              Account
            </span>
            {openSection === "account" ? (
              <ChevronDown size={17} />
            ) : (
              <ChevronRight size={17} />
            )}
          </button>

          {openSection === "account" && (
            <div className="account-subtabs">
              <button
                className={activeTab === "profile" ? "active" : ""}
                onClick={() => selectTab("account", "profile")}
              >
                <span className="sub-dot" />
                Profile
              </button>

              <button
                className={activeTab === "security" ? "active" : ""}
                onClick={() => selectTab("account", "security")}
              >
                <span className="sub-dot" />
                Security
              </button>
            </div>
          )}

          {/* MAIN TAB 2 */}
          <button
            className={`account-main-tab ${
              openSection === "workspace" ? "open" : ""
            }`}
            onClick={() =>
              setOpenSection(
                openSection === "workspace" ? "account" : "workspace"
              )
            }
          >
            <span className="account-main-label">
              <Building2 size={18} />
              Workspace
            </span>
            {openSection === "workspace" ? (
              <ChevronDown size={17} />
            ) : (
              <ChevronRight size={17} />
            )}
          </button>

          {openSection === "workspace" && (
            <div className="account-subtabs">
              <button
                className={activeTab === "business" ? "active" : ""}
                onClick={() => selectTab("workspace", "business")}
              >
                <span className="sub-dot" />
                Business details
              </button>

              <button
                className={activeTab === "preferences" ? "active" : ""}
                onClick={() => selectTab("workspace", "preferences")}
              >
                <span className="sub-dot" />
                Preferences
              </button>
            </div>
          )}
        </div>

        <div className="account-sidebar-bottom">
          <button>
            <Settings size={17} />
            Settings
          </button>

          <button>
            <LogOut size={17} />
            Log out
          </button>
        </div>
      </aside>
{sidebarOpen && (
  <div
    className="account-sidebar-overlay"
    onClick={() => setSidebarOpen(false)}
  />
)}
      <main className="account-main">
        <button
  className="account-mobile-menu"
  onClick={() => setSidebarOpen(true)}
  aria-label="Open sidebar"
>
  <Menu size={21} />
</button>
        <header className="account-topbar">
          <div className="account-topbar-title">
            <span className="account-topbar-icon">
              <MessageSquare size={17} />
            </span>
            <span>Account</span>
          </div>

          <button className="account-avatar">
            <User size={17} />
          </button>
        </header>

        <section className="account-content">
          <div className="account-content-inner">
            {activeTab === "profile" && (
              <>
                <span className="account-eyebrow">ACCOUNT</span>
                <h1>Profile</h1>
                <p className="account-description">
                  Manage your personal account information.
                </p>

                <div className="account-card">
                  <div className="account-card-icon">
                    <User size={20} />
                  </div>
                  <div>
                    <h3>Your profile</h3>
                    <p>
                      Your name, phone number and other account information
                      will appear here.
                    </p>
                  </div>
                </div>
              </>
            )}

            {activeTab === "security" && (
              <>
                <span className="account-eyebrow">ACCOUNT</span>
                <h1>Security</h1>
                <p className="account-description">
                  Manage your password and account security.
                </p>

                <div className="account-card">
                  <div className="account-card-icon">
                    <Shield size={20} />
                  </div>
                  <div>
                    <h3>Security settings</h3>
                    <p>
                      Password, login sessions and security controls will be
                      managed here.
                    </p>
                  </div>
                </div>
              </>
            )}

            {activeTab === "business" && (
              <>
                <span className="account-eyebrow">WORKSPACE</span>
                <h1>Business details</h1>
                <p className="account-description">
                  Manage the business information used by ConvoTrain.
                </p>

                <div className="account-card">
                  <div className="account-card-icon">
                    <Building2 size={20} />
                  </div>
                  <div>
                    <h3>Business information</h3>
                    <p>
                      Restaurant name, address, contact details and other
                      business information will appear here.
                    </p>
                  </div>
                </div>
              </>
            )}

            {activeTab === "preferences" && (
              <>
                <span className="account-eyebrow">WORKSPACE</span>
                <h1>Preferences</h1>
                <p className="account-description">
                  Manage how your ConvoTrain workspace behaves.
                </p>

                <div className="account-card">
                  <div className="account-card-icon">
                    <Settings size={20} />
                  </div>
                  <div>
                    <h3>Workspace preferences</h3>
                    <p>
                      Workspace settings and preferences will be added here
                      later.
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="account-chatbar">
            <button>
              <Plus size={18} />
            </button>
            <input
              type="text"
              placeholder="Ask ConvoTrain anything..."
            />
            <span>Account assistant</span>
          </div>
        </section>
      </main>
    </div>
  );
}
