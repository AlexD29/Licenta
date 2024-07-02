import React from "react";
import Entities from "./Entities";

const City = ({userId}) => {
  return <Entities userId={userId} entityType="city" apiUrl="http://localhost:8000/api/cities_articles" />;
};

export default City;
