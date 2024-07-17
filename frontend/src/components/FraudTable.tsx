import React, { useEffect, useState } from 'react';
import type { TableColumnsType } from 'antd';
import { ConfigProvider, Table, Tag } from 'antd';

interface DataType {
  key: React.Key;
  client: string;
  frauds: string[];
}

interface ExpandedDataType {
  key: React.Key;
  date: string;
  card: string;
  date_of_birth: string;
  passport: string;
  passport_valid_to: string;
  phone: string;
  operation_type: string;
  amount: number;
  operation_result: string;
  terminal_type: string;
  city: string;
  address: string;
  passport_validity_fraud: boolean;
  time_diff_fraud: boolean;
  address_diff_fraud: boolean;
  city_diff_fraud: boolean;
  data_discrepancy_fraud: boolean;
  amount_outlier_fraud: boolean;
  alg_fraud_status: boolean;
  ml_fraud_status: boolean;
}

function FraudTable(data: any) {
  if (data.data == null) {
    return null;
  }

  const [currentData, setCurrentData] = useState<DataType[]>([]);
  const [transactionsMap, setTransactionsMap] = useState<Map<string, ExpandedDataType[]>>(new Map());

  useEffect(() => {
    const newData = data.data;
    const clientMap = new Map<string, ExpandedDataType[]>();

    newData.forEach((item: any) => {
      const client = item.client;
      if (!clientMap.has(client)) {
        clientMap.set(client, []);
      }
      clientMap.get(client)!.push(item);
    });

    const updatedClientData = Array.from(clientMap.keys()).map((client, index) => {
      const fraudTags = Array.from(new Set(
        clientMap.get(client)!.flatMap((item: any) =>
          Object.keys(item).filter(key => (key.endsWith('_fraud') || key === 'ml_fraud_status') && item[key])
        )
      ));
      return { key: index.toString(), client, frauds: fraudTags };
    });

    setCurrentData(updatedClientData);
    setTransactionsMap(clientMap);
  }, [data]);

  const renameFraudTag = (fraudTag: string) => {
    switch (fraudTag) {
      case 'alg_fraud_status':
        return '';
      case 'ml_fraud_status':
        return 'Anomaly';
      case 'passport_validity_fraud':
        return 'Passport validity';
      case 'time_diff_fraud':
        return 'Time difference';
      case 'address_diff_fraud':
        return 'Address difference';
      case 'city_diff_fraud':
        return 'City difference';
      case 'data_discrepancy_fraud':
        return 'Data discrepancy';
      case 'amount_outlier_fraud':
        return 'Amount outlier';
      default:
        return fraudTag;
    }
  };

  const getTagColor = (fraudTag: string) => {
    switch (fraudTag) {
      case 'ml_fraud_status':
        return 'blue';
      case 'alg_fraud_status':
        return 'geekblue';
      case 'passport_validity_fraud':
        return 'purple';
      case 'time_diff_fraud':
        return 'cyan';
      case 'address_diff_fraud':
        return 'magenta';
      case 'city_diff_fraud':
        return 'red';
      case 'data_discrepancy_fraud':
        return 'orange';
      case 'amount_outlier_fraud':
        return 'lime';
      default:
        return 'red'; 
    }
  };

  const expandedRowRender = (record: DataType) => {
    const columns: TableColumnsType<ExpandedDataType> = [
      { title: 'Date', dataIndex: 'date', key: 'date' },
      { title: 'Card', dataIndex: 'card', key: 'card' },
      { title: 'Date of birth', dataIndex: 'date_of_birth', key: 'date_of_birth' },
      { title: 'Passport', dataIndex: 'passport', key: 'passport' },
      { title: 'Passport valid to', dataIndex: 'passport_valid_to', key: 'passport_valid_to' },
      { title: 'Phone', dataIndex: 'phone', key: 'phone' },
      { title: 'Operation type', dataIndex: 'operation_type', key: 'operation_type' },
      { title: 'Amount', dataIndex: 'amount', key: 'amount' },
      { title: 'Operation result', dataIndex: 'operation_result', key: 'operation_result' },
      { title: 'Terminal type', dataIndex: 'terminal_type', key: 'terminal_type' },
      { title: 'City', dataIndex: 'city', key: 'city' },
      { title: 'Address', dataIndex: 'address', key: 'address' },
      {
        title: 'Frauds',
        dataIndex: 'frauds',
        key: 'frauds',
        render: (_, record) => (
          <>
            {Object.entries(record).map(([key, value]) => {
              if ((key.endsWith('_fraud') || key === 'ml_fraud_status') && value) {
                return <Tag key={key} color={getTagColor(key)}>{renameFraudTag(key)}</Tag>;
              }
              return null;
            })}
          </>
        ),
      },
    ];

    const currentExpandedData = transactionsMap.get(record.client) || [];
    return <Table columns={columns} dataSource={currentExpandedData} pagination={false} />;
  };

  const columns: TableColumnsType<DataType> = [
    { title: 'Client', dataIndex: 'client', key: 'client', fixed: 'left' },
    {
      title: 'Fraud tags',
      dataIndex: 'frauds',
      key: 'frauds',
      fixed: 'right',
      render: (frauds: string[]) => (
        <>
          {frauds.map(fraud => (
            <Tag key={fraud} color={getTagColor(fraud)}>{renameFraudTag(fraud)}</Tag>
          ))}
        </>
      ),
    },
  ];

  const tableStyles = {
    position: 'relative' as 'relative',
  };

  return (
    <ConfigProvider
      theme={{
        components: {
          Table: {
            colorBgContainer: "#333333",
            colorText: "#bdbdbd",
            colorTextHeading: "#bdbdbd",
            borderColor: "#bdbdbd",
            colorLinkHover: "#50c777",
          },
          Pagination: {
            colorBgContainer: "#333333",
            colorText: "#bdbdbd",
            colorTextHeading: "#bdbdbd",
            colorLinkHover: "#50c777",
            controlItemBgActive: "#50c777",
            colorPrimary: "#50c777",
            colorPrimaryHover: "#50c777",
          },
        },
      }}
    >
      <Table
        columns={columns}
        expandable={{ expandedRowRender, defaultExpandedRowKeys: [], expandRowByClick: true }}
        dataSource={currentData}
        size="large"
        scroll={{ x: '100%' }}
        style={tableStyles}
        rowClassName={() => 'table-row'}
        pagination={{
          defaultPageSize: 20,
          position: ['bottomCenter']              
        }}
      />
    </ConfigProvider>
  );
}

export default FraudTable;