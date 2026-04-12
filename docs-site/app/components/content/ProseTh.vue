<template>
  <th>
    <slot />
  </th>
</template>

<style scoped>
th {
  text-align: left;
  padding: 0.6rem 1rem;
  border-bottom: 2px solid var(--color-gray-200);
  font-weight: 600;
  white-space: nowrap;
}
</style>
