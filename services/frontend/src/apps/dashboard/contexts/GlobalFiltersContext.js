import { createContext, useContext } from "react";

// 建立全域篩選器 Context
export const GlobalFiltersContext = createContext();

export const useGlobalFilters = () => {
  const context = useContext(GlobalFiltersContext);
  if (!context) {
    throw new Error("useGlobalFilters must be used within Layout");
  }
  return context;
};
