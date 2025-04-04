// src/app/utils/formatters.ts

export const formatCourseId = (rawCourseId: string): string => {
    const parts = rawCourseId.split('_');
    if (parts.length >= 2) {
      return `${parts[0]} ${parts[1]}`;
    }
    return rawCourseId;
  };
  