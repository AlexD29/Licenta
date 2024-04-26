import React from 'react';
import { useParams } from 'react-router-dom';

function ArticleDetail() {
  const { id } = useParams();

  // Fetch article details based on the ID
  // Display article details

  return (
    <div>
      <h2>Article Detail</h2>
      <p>Article ID: {id}</p>
      {/* Fetch and display article details based on the ID */}
    </div>
  );
}

export default ArticleDetail;
