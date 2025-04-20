// src/app/instructor/metrics.tsx
'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../../constants';
import SignOutButton from '../../components/SignOutButton';
import { useRouter } from 'next/navigation';
import { jsPDF } from 'jspdf';

const MetricsPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [params, setParams] = useState({
    topAskX: 5,
    topAnsY: 5,
    minLength: 50,
    includeWords: '',
    excludeWords: '',
    includeComments: false,
    commonWordB: 10,
    topTagCount: 5,
    topViewedK: 5,
  });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return alert('Please select a JSON file');
    setLoading(true);
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      const body = {
        data,
        params: {
          topAskX: params.topAskX,
          topAnsY: params.topAnsY,
          answerFilters: {
            minLength: params.minLength,
            includeWords: params.includeWords
              .split(',')
              .map(w => w.trim())
              .filter(Boolean),
            excludeWords: params.excludeWords
              .split(',')
              .map(w => w.trim())
              .filter(Boolean),
            requireEndorsed: true,
            includeComments: params.includeComments,
          },
          commonWordB: params.commonWordB,
          topTagCount: params.topTagCount,
          topViewedK: params.topViewedK,
        },
      };

      const res = await axios.post(
        `${API_ENDPOINTS.BACKEND_URL}/edstem/metrics`,
        body,
        { withCredentials: true }
      );
      setResults(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to compute metrics.');
    } finally {
      setLoading(false);
    }
  };

  // CSV Export (unchanged)
  const exportCSV = () => {
    if (!results) return;
    const sections = [
      { key: 'topAskers',    label: 'Top Askers',    cols: ['name','count'] },
      { key: 'topAnswerers', label: 'Top Answerers', cols: ['name','count'] },
      { key: 'commonWords',  label: 'Common Words',  cols: ['word','count'] },
      { key: 'commonTags',   label: 'Common Tags',   cols: ['tag','count'] },
    ];
    let csv = '';
    sections.forEach(({ key, label, cols }) => {
      csv += `${label}\n${cols.join(',')}\n`;
      results[key].forEach((row: any) => {
        csv += cols.map(c => row[c]).join(',') + '\n';
      });
      csv += '\n';
    });
    csv += 'Most Viewed Posts\nurl,title,views\n';
    results.mostViewed.forEach((p: any) => {
      csv += `${p.url},"${(p.title || p.number).replace(/"/g,'""')}",${p.views}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'edstem_metrics.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // PDF Export (unchanged)
  const exportPDF = () => {
    if (!results) return;
    const doc = new jsPDF();
    let y = 10;
    const addSection = (title: string, lines: string[]) => {
      doc.setFontSize(14);
      doc.text(title, 10, y); y += 8;
      doc.setFontSize(11);
      lines.forEach(line => {
        doc.text(line, 12, y); 
        y += 6;
        if (y > 280) { doc.addPage(); y = 10; }
      });
      y += 6;
    };
    addSection(
      'Top Askers',
      results.topAskers.map((u: any) => `${u.name} — ${u.count}`)
    );
    addSection(
      'Top Answerers',
      results.topAnswerers.map((u: any) => `${u.name} — ${u.count}`)
    );
    addSection(
      'Common Words',
      results.commonWords.map((w: any) => `${w.word} — ${w.count}`)
    );
    addSection(
      'Common Tags',
      results.commonTags.map((t: any) => `${t.tag} — ${t.count}`)
    );
    addSection(
      'Most Viewed',
      results.mostViewed.map((p: any) => `${p.title||p.number} — ${p.views} views`)
    );
    doc.save('edstem_metrics.pdf');
  };

  return (
    <div className="min-h-screen bg-[#0e1c2c]/75 text-white p-8">
      <div className="flex justify-end mb-4">
        <SignOutButton />
      </div>
      <h1 className="text-4xl font-bold mb-6">Compute EdStem Metrics</h1>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* file upload */}
        <div className="col-span-full">
          <label className="block font-medium">Upload JSON File</label>
          <input
            type="file"
            accept="application/json"
            onChange={e => setFile(e.target.files?.[0] ?? null)}
            className="mt-2 p-2 bg-white text-black rounded w-full"
          />
        </div>

        {/* metric parameters */}
        {/* … inputs for topAskX, topAnsY, etc. */}
        <label>
          Top Askers (x):
          <input type="number" value={params.topAskX}
            onChange={e => setParams(p => ({ ...p, topAskX: +e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label>
          Top Answerers (y):
          <input type="number" value={params.topAnsY}
            onChange={e => setParams(p => ({ ...p, topAnsY: +e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label>
          Min Answer Length:
          <input type="number" value={params.minLength}
            onChange={e => setParams(p => ({ ...p, minLength: +e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label>
          Include Words (comma‑sep):
          <input type="text" value={params.includeWords}
            onChange={e => setParams(p => ({ ...p, includeWords: e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label>
          Exclude Words (comma‑sep):
          <input type="text" value={params.excludeWords}
            onChange={e => setParams(p => ({ ...p, excludeWords: e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label className="flex items-center space-x-2">
          <input type="checkbox" checked={params.includeComments}
            onChange={e => setParams(p => ({ ...p, includeComments: e.target.checked }))}
            className="w-5 h-5" />
          <span>Include comments in answer counts</span>
        </label>
        <label>
          Top Common Words (b):
          <input type="number" value={params.commonWordB}
            onChange={e => setParams(p => ({ ...p, commonWordB: +e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label>
          Top Tag Count:
          <input type="number" value={params.topTagCount}
            onChange={e => setParams(p => ({ ...p, topTagCount: +e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>
        <label>
          Top Viewed Posts (k):
          <input type="number" value={params.topViewedK}
            onChange={e => setParams(p => ({ ...p, topViewedK: +e.target.value }))}
            className="mt-1 p-2 bg-white text-black rounded w-full" />
        </label>

        {/* form buttons */}
        <div className="col-span-full flex justify-between items-center">
          <button type="button"
            onClick={() => router.push('/instructor')}
            className="px-4 py-2 bg-gray-600 rounded hover:bg-gray-700">
            Back
          </button>
          <button type="submit" disabled={loading}
            className="px-6 py-3 bg-green-600 rounded hover:bg-green-700 disabled:opacity-50">
            {loading ? 'Computing…' : 'Compute Metrics'}
          </button>
        </div>
      </form>

      {results && (
        <div className="mt-10 space-y-8">
          {/* export buttons */}
          <div className="flex gap-4">
            <button onClick={exportCSV}
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
              Export CSV
            </button>
            <button onClick={exportPDF}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700">
              Export PDF
            </button>
          </div>

          {/* Top Askers */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">Top Askers</h2>
            <ol className="list-decimal pl-6 space-y-1">
              {results.topAskers.map((u: any, i: number) => (
                <li key={i}>{u.name} — {u.count}</li>
              ))}
            </ol>
          </section>

          {/* Top Answerers */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">Top Answerers</h2>
            <ol className="list-decimal pl-6 space-y-1">
              {results.topAnswerers.map((u: any, i: number) => (
                <li key={i}>{u.name} — {u.count}</li>
              ))}
            </ol>
          </section>

          {/* Common Words */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">Common Words</h2>
            <ol className="list-decimal pl-6 space-y-1">
              {results.commonWords.map((w: any, i: number) => (
                <li key={i}>{w.word} — {w.count}</li>
              ))}
            </ol>
          </section>

          {/* Common Tags */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">Common Tags</h2>
            <ol className="list-decimal pl-6 space-y-1">
              {results.commonTags.map((t: any, i: number) => (
                <li key={i}>{t.tag} — {t.count}</li>
              ))}
            </ol>
          </section>

          {/* Most Viewed Posts with hyperlinks */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">Most Viewed Posts</h2>
            <ul className="space-y-2">
              {results.mostViewed.map((p: any, i: number) => (
                <li key={i} className="bg-white text-black p-3 rounded">
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-blue-800 hover:underline"
                  >
                    {p.title || `Post #${p.number}`}
                  </a>
                  <div>Views: {p.views}</div>
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
};

export default MetricsPage;
