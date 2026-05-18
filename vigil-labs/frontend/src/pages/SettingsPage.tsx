import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, User, Shield, Database, Download, Upload, Moon, Monitor } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Moon },
    { id: 'data', label: 'Data & Export', icon: Database },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-vigil-text">Settings</h1>
        <p className="text-sm text-vigil-text-muted">Manage your account and preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Settings Sidebar */}
        <div className="w-48 space-y-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                activeTab === tab.id
                  ? 'bg-vigil-primary/10 text-vigil-primary border border-vigil-primary/20'
                  : 'text-vigil-text-muted hover:text-vigil-text hover:bg-vigil-hover'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 glass-panel p-6">
          {activeTab === 'profile' && (
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-vigil-text">Profile Settings</h3>
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-vigil-primary to-vigil-accent flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">{user?.username?.[0]?.toUpperCase()}</span>
                </div>
                <div>
                  <p className="font-medium text-vigil-text">{user?.display_name || user?.username}</p>
                  <p className="text-sm text-vigil-text-muted">Role: {user?.role}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Username</label>
                  <input type="text" value={user?.username || ''} readOnly className="input-field opacity-60" />
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Email</label>
                  <input type="email" defaultValue={user?.email || ''} className="input-field" placeholder="your@email.com" />
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Display Name</label>
                  <input type="text" defaultValue={user?.display_name || ''} className="input-field" />
                </div>
                <button className="btn-primary">Save Changes</button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-vigil-text">Security Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Current Password</label>
                  <input type="password" className="input-field" placeholder="Enter current password" />
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">New Password</label>
                  <input type="password" className="input-field" placeholder="Enter new password" />
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Confirm Password</label>
                  <input type="password" className="input-field" placeholder="Confirm new password" />
                </div>
                <button className="btn-primary">Update Password</button>
              </div>

              <div className="pt-4 border-t border-vigil-border">
                <h4 className="font-medium text-vigil-text mb-3">Session Settings</h4>
                <div className="flex items-center justify-between p-3 rounded-lg bg-vigil-bg">
                  <div>
                    <p className="text-sm text-vigil-text">Inactivity Lock</p>
                    <p className="text-xs text-vigil-text-dim">Auto-lock after 30 minutes of inactivity</p>
                  </div>
                  <div className="w-10 h-5 rounded-full bg-vigil-primary relative cursor-pointer">
                    <div className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-white" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-vigil-text">Appearance</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-4 rounded-lg bg-vigil-bg border-2 border-vigil-primary text-center cursor-pointer">
                    <Moon size={24} className="mx-auto text-vigil-primary mb-2" />
                    <span className="text-xs text-vigil-text">Dark (Active)</span>
                  </div>
                  <div className="p-4 rounded-lg bg-vigil-bg border border-vigil-border text-center cursor-pointer opacity-50">
                    <Monitor size={24} className="mx-auto text-vigil-text-dim mb-2" />
                    <span className="text-xs text-vigil-text-dim">Light (Soon)</span>
                  </div>
                  <div className="p-4 rounded-lg bg-vigil-bg border border-vigil-border text-center cursor-pointer opacity-50">
                    <Monitor size={24} className="mx-auto text-vigil-text-dim mb-2" />
                    <span className="text-xs text-vigil-text-dim">System (Soon)</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-vigil-text">Data Management</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 rounded-lg bg-vigil-bg border border-vigil-border">
                  <div>
                    <p className="text-sm font-medium text-vigil-text">Export All Tools</p>
                    <p className="text-xs text-vigil-text-dim">Download tool configurations as JSON</p>
                  </div>
                  <button className="btn-secondary text-sm flex items-center gap-2">
                    <Download size={14} /> Export
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg bg-vigil-bg border border-vigil-border">
                  <div>
                    <p className="text-sm font-medium text-vigil-text">Import Tools</p>
                    <p className="text-xs text-vigil-text-dim">Import tool configurations from JSON</p>
                  </div>
                  <button className="btn-secondary text-sm flex items-center gap-2">
                    <Upload size={14} /> Import
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg bg-vigil-bg border border-vigil-border">
                  <div>
                    <p className="text-sm font-medium text-vigil-text">Export History</p>
                    <p className="text-xs text-vigil-text-dim">Export all execution history</p>
                  </div>
                  <button className="btn-secondary text-sm flex items-center gap-2">
                    <Download size={14} /> Export
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
