import { useState } from 'react';

import DropFileInput from './components/DropFileInput'
import FraudTable from './components/FraudTable'


function App() {

  const [data, setData] = useState<any>(null);
  const [precision, setPrecision] = useState<number | null>(null);
  const [recall, setRecall] = useState<number | null>(null);
  const [transactionsAmount, setTransactionsAmount] = useState<number | null>(null);
  const [frTransactionsAmount, setFrTransactionsAmount] = useState<number | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const fetchData = async () => {
    await fetch(`http://localhost:${import.meta.env.VITE_APP_API_PORT}/transactions/`, {method: "GET"}).then(
      (response) => {
        return response.json();
      }
    ).then(
      (response) => {
        fetchMetrics();
        setData(response);
        console.log(response);
      }
    )
  }

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`http://localhost:${import.meta.env.VITE_APP_API_PORT}/fetchmetrics/`);
      if (!response.ok) {
        throw new Error('Failed to fetch metrics');
      }
      const metricsData = await response.json();
      setPrecision(metricsData.precision);
      setRecall(metricsData.recall);
      setTransactionsAmount(metricsData.overall_transactions);
      setFrTransactionsAmount(metricsData.fraudlent_transactions);
      const currentDate = new Date();
      const formattedDate = currentDate.toLocaleString()
      setLastUpdated(formattedDate);
      console.log('Metrics data:', metricsData);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  } 

  return (
    <div className="App flex items-center justify-center min-h-screen">
      <div className="w-4/5">
        <div className="mb-8">
          <DropFileInput callback={fetchData} />
        </div>

        <div className="mb-4 flex">
          <div className="mr-10 text-white-750 text-xl">Precision: {precision}</div>
          <div className="mr-10 text-white-750 text-xl">Recall: {recall}</div>
          <div className="mr-10 text-white-750 text-xl">Transactions: {transactionsAmount}</div>
          <div className="mr-10 text-white-750 text-xl">Fraudlent: {frTransactionsAmount}</div>
          <div className="mr-10 text-white-750 text-xl">Last updated: {lastUpdated}</div>
        </div>


        <div className="mb-8 shadow-[5px_5px_5px_rgba(0,0,0,0.75)]">
          <FraudTable data={data} />
        </div>
      </div>
    </div>
  )
}

export default App;
