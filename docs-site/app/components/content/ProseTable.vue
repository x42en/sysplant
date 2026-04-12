<template>
  <div class="prose-table-wrapper">
    <table>
      <slot />
    </table>
  </div>
</template>

<style scoped>
.prose-table-wrapper {
  overflow-x: auto;
  margin: 1.5rem 0;
}
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.95em;
}
</style>
