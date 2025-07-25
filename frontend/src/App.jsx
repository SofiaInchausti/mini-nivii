import { useMemo, useState, useEffect } from 'react'
import ChartRenderer from './ChartRenderer'
import './App.css'
import './index.css'
import React from 'react'

function ChatInput({ onSend }) {
  const [value, setValue] = useState("");
  return (
    <form className="flex gap-2 p-4 border-t" onSubmit={e => { e.preventDefault(); if (value.trim()) { onSend(value); setValue(""); } }}>
      <input
        className="text-gray-800 flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm transition placeholder-gray-400 bg-gray-50"
        type="text"
        placeholder="Make a question..."
        value={value}
        onChange={e => setValue(e.target.value)}
      />
      <button
        type="submit"
        className="rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold px-5 py-2 shadow transition"
      >
        Send
      </button>
    </form>
  )
}

function ChatMain({ history }) {
  return (
    <section className="flex-1 flex flex-col justify-between h-full  text-gray-800 font-semibold">
      <div className="flex-1 p-8 overflow-y-auto space-y-6">
        {history.length === 0 ? (
          <div className="text-gray-400 text-center mt-20">Ask a question to get started.</div>
        ) : (
          history.map((item, idx) => (
            <div key={idx} className="mb-4">
              <div className="shadow-md border border-gray-200 rounded-lg p-4 bg-white">
              <div className="py-5 shadow-lg mb-8 px-4 rounded-[18px] flex justify-around">
                  <div className="">{item.question}</div>
                </div>
          
                <div className="bg-green-50 p-2 rounded text-gray-900">
                  <span>{item?.answer?.summary}</span>
                  {item?.chart && item.chart_data && item.chart_data.labels && item.chart_data.datasets && item.chart_data.labels.length > 0 && item.chart_data.datasets.length > 0 && (
                    <ChartRenderer
                      chartType={item.chart}
                      data={{
                        labels: item.chart_data.labels,
                        datasets: item.chart_data.datasets
                      }}
                      options={{
                        responsive: true,
                        plugins: {
                          legend: { position: 'top' },
                          title: { display: true, text: 'Monthly Sales' }
                        }
                      }}
                    />
                  )}
                  {item.pending && <span className="ml-2 animate-pulse text-gray-400">...</span>}
                </div>
              </div>
            </div>

          ))
        )}
      </div>
    </section>
  )
}

function App() {
  const [history, setHistory] = useState([])
  const current = history[history.length - 1]

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        console.log(data)
        if (Array.isArray(data)) setHistory(data)
      })
      .catch(() => setHistory([]))
  }, [])

  function handleSend(question) {
    // Crea un objeto "pending" con la misma estructura que el backend
    const pendingMsg = {
      id: null,
      question,
      sql_query: null,
      result: [],
      date: null,
      chart: null,
      chart_data: { labels: [], datasets: [] },
      answer: { summary: 'Cargando...' },
      pending: true
    };
    setHistory(prev => [...prev, pendingMsg]);

    fetch('http://localhost:8000/responses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    })
      .then(res => res.ok ? res.json() : Promise.reject())
      .then(data => {
        setHistory(prev => {
          const updated = [...prev];
          const idx = updated.map(m => m.pending).lastIndexOf(true);
          if (idx !== -1) {
            updated[idx] = {
              id: data.id ?? null,
              question: prev[idx].question ?? data.question ?? '',
              sql_query: data.sql_query ?? null,
              result: data.result ?? [],
              date: data.date ?? null,
              chart: data.chart ?? null,
              chart_data: data.chart_data ?? { labels: [], datasets: [] },
              answer: data.answer ?? { summary: '' },
              pending: false
            };
          }
          return updated;
        });
      })
      .catch(() => {
        setHistory(prev => {
          const updated = [...prev];
          const idx = updated.map(m => m.pending).lastIndexOf(true);
          if (idx !== -1) {
            updated[idx] = {
              ...updated[idx],
              answer: { summary: 'Error al obtener respuesta' },
              pending: false
            };
          }
          return updated;
        });
      });
  }

  const totalResultados = useMemo(() => {
    return history.reduce((acc, item) => {
      if (Array.isArray(item.result) && item.result.length > 0) {
        return acc + item.result.length;
      }
      return acc;
    }, 0);
  }, [history]);

  return (
    <div className="flex h-screen">
      <div className="w-full flex flex-col h-full">
        <ChatMain history={history} />
        <ChatInput onSend={handleSend} />
      </div>
    </div>
  )
}

export default App
